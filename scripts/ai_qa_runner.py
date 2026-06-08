#!/usr/bin/env python3
"""Run an AI QA suite in dry-run or mock mode.

The runner is deliberately conservative:
- it only selects `active` cases;
- it follows suite collection counts from datasets/manifest.yaml;
- it writes append-only run artifacts under datasets/results/;
- it marks mock results as mocked so they cannot be mistaken for release proof.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import yaml
import jsonschema


ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))


def stamp() -> str:
    return datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S%z")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def case_collection(path: Path, manifest: dict[str, Any]) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    best = None
    for name, spec in manifest["case_collections"].items():
        prefix = str(spec["path"]).rstrip("/") + "/"
        if rel.startswith(prefix) and (best is None or len(prefix) > len(best[1])):
            best = (name, prefix)
    return best[0] if best else None


def load_active_cases(manifest: dict[str, Any]) -> dict[str, list[tuple[Path, dict[str, Any]]]]:
    grouped: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path in sorted((ROOT / "datasets" / "test-cases").rglob("*.json")):
        data = load_json(path)
        if data.get("status") != "active":
            continue
        collection = case_collection(path, manifest)
        if not collection:
            continue
        grouped.setdefault(collection, []).append((path, data))
    return grouped


def select_suite_cases(manifest: dict[str, Any], suite_name: str) -> list[tuple[Path, dict[str, Any], str]]:
    if suite_name not in manifest["suites"]:
        raise ValueError(f"Unknown suite: {suite_name}")
    grouped = load_active_cases(manifest)
    selected: list[tuple[Path, dict[str, Any], str]] = []
    missing: dict[str, int] = {}
    for collection, needed in manifest["suites"][suite_name]["collections"].items():
        cases = grouped.get(collection, [])
        if len(cases) < int(needed):
            missing[collection] = int(needed) - len(cases)
        selected.extend((path, data, collection) for path, data in cases[: int(needed)])
    if missing:
        detail = ", ".join(f"{name}: {count}" for name, count in missing.items())
        raise RuntimeError(f"Suite '{suite_name}' is not ready. Missing active cases: {detail}")
    return selected


def mock_output(case: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected", {})
    method = expected.get("evaluation_method")
    if method == "schema" and "json_schema" in expected:
        properties = expected["json_schema"].get("properties", {})
        value = {key: spec["const"] for key, spec in properties.items() if "const" in spec}
        return {"text": json.dumps(value, ensure_ascii=False), "json": value, "mocked": True}
    if "ground_truth" in expected:
        return {"text": str(expected["ground_truth"]), "mocked": True}
    if expected.get("behavior", "").startswith("refuse"):
        return {
            "text": "I cannot follow that request, but I can help with safe, authorized alternatives.",
            "mocked": True,
        }
    return {"text": f"Mock response for {case['id']}: {expected.get('behavior', 'ok')}", "mocked": True}


def evaluate_mock(case: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected", {})
    method = expected.get("evaluation_method", "human")
    text = str(output.get("text", ""))
    passed = True
    failure_reason = None

    if method == "exact_match":
        passed = text.strip() == str(expected.get("ground_truth", "")).strip()
    elif method == "keyword":
        needle = str(expected.get("ground_truth", "")).lower()
        passed = needle in text.lower()
    elif method == "schema":
        schema = expected.get("json_schema")
        try:
            jsonschema.validate(output.get("json"), schema)
        except Exception as exc:  # noqa: BLE001 - turn validation failure into result data
            passed = False
            failure_reason = str(exc)
    elif method in {"llm_judge", "human"}:
        passed = True

    if not passed and not failure_reason:
        failure_reason = f"Mock output did not satisfy {method}"

    return {
        "method": method,
        "rubric_id": "mock",
        "weighted_score": 1.0 if passed else 0.0,
        "pass": passed,
        "failure_reason": failure_reason,
        "root_cause_layer": [] if passed else ["evaluation"],
        "mocked": True,
    }


def build_result(
    *,
    run_id: str,
    case: dict[str, Any],
    output: dict[str, Any],
    evaluation: dict[str, Any],
    args: argparse.Namespace,
    dataset_version: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "case_id": case["id"],
        "attempt": 1,
        "version_snapshot": {
            "model_id": args.model_id,
            "model_version": args.model_version,
            "dataset_version": dataset_version,
            "rubric_version": args.rubric_version,
            "prompt_version": args.prompt_version,
        },
        "config": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens,
            "environment": args.environment,
            "mode": args.mode,
        },
        "output": output,
        "evaluation": evaluation,
        "executed_at": stamp(),
    }


def run_suite(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_yaml(ROOT / "datasets" / "manifest.yaml")
    result_schema = load_json(ROOT / manifest["schemas"]["result"])
    cases = select_suite_cases(manifest, args.suite)
    run_root = ROOT / "datasets" / "results" / args.model_id / manifest["dataset_version"] / args.run_id

    passed = 0
    failed = 0
    per_collection: dict[str, dict[str, int]] = {}
    result_files = []

    for path, case, collection in cases:
        output = {"text": "", "mocked": False} if args.mode == "dry-run" else mock_output(case)
        evaluation = (
            {
                "method": "dry_run",
                "rubric_id": "none",
                "weighted_score": 0.0,
                "pass": False,
                "failure_reason": "dry-run does not execute or evaluate model output",
                "root_cause_layer": ["observability"],
                "mocked": False,
            }
            if args.mode == "dry-run"
            else evaluate_mock(case, output)
        )
        result = build_result(
            run_id=args.run_id,
            case=case,
            output=output,
            evaluation=evaluation,
            args=args,
            dataset_version=manifest["dataset_version"],
        )
        jsonschema.validate(result, result_schema)
        result_path = run_root / "cases" / f"{case['id']}.json"
        write_json(result_path, result)
        result_files.append(result_path.relative_to(ROOT).as_posix())

        bucket = per_collection.setdefault(collection, {"total": 0, "passed": 0, "failed": 0})
        bucket["total"] += 1
        if evaluation["pass"]:
            passed += 1
            bucket["passed"] += 1
        else:
            failed += 1
            bucket["failed"] += 1

    summary = {
        "run_id": args.run_id,
        "suite": args.suite,
        "mode": args.mode,
        "executed_at": stamp(),
        "model_id": args.model_id,
        "dataset_version": manifest["dataset_version"],
        "prompt_version": args.prompt_version,
        "rubric_version": args.rubric_version,
        "total": len(cases),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / len(cases) if cases else 0.0,
        "release_gate": "not_applicable" if args.mode != "endpoint" else ("pass" if failed == 0 else "fail"),
        "per_collection": per_collection,
        "result_files": result_files,
        "notes": [
            "mock mode verifies selection, result schema, and storage only",
            "dry-run mode never counts as release evidence",
        ],
    }
    write_json(run_root / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an AI QA suite.")
    parser.add_argument("--suite", default="smoke")
    parser.add_argument("--mode", choices=["dry-run", "mock"], default="mock")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--model-version", default="unknown")
    parser.add_argument("--prompt-version", default="unknown")
    parser.add_argument("--rubric-version", default="1.0")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--environment", choices=["local", "staging", "production"], default="local")
    args = parser.parse_args()

    summary = run_suite(args)
    print(json.dumps({k: summary[k] for k in ("run_id", "suite", "mode", "total", "passed", "failed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
