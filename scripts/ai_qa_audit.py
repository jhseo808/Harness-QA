#!/usr/bin/env python3
"""Audit AI QA dataset readiness against datasets/manifest.yaml.

This is intentionally read-only. It validates JSON test cases, checks suite
coverage, and reports whether each suite has enough active cases to be used as
a release gate.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import yaml

try:
    import jsonschema
except ImportError:  # pragma: no cover - handled at runtime for lean envs
    jsonschema = None


ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))


@dataclass(frozen=True)
class CaseRecord:
    path: Path
    data: dict[str, Any]
    collection: str | None
    schema_errors: list[str]

    @property
    def status(self) -> str:
        return str(self.data.get("status", "missing"))

    @property
    def risk_level(self) -> str:
        return str(self.data.get("risk_level", "missing"))

    @property
    def case_id(self) -> str:
        return str(self.data.get("id", self.path.name))


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_collection(path: Path, collections: dict[str, Any]) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    matches = []
    for name, spec in collections.items():
        prefix = str(spec["path"]).rstrip("/") + "/"
        if rel.startswith(prefix):
            matches.append((name, len(prefix)))
    if not matches:
        return None
    matches.sort(key=lambda item: item[1], reverse=True)
    return matches[0][0]


def validate_case(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    if jsonschema is None:
        return ["jsonschema package is not installed"]
    validator = jsonschema.Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(data), key=lambda e: e.path)]


def collect_cases(root: Path, manifest: dict[str, Any], schema: dict[str, Any]) -> list[CaseRecord]:
    collections = manifest.get("case_collections", {})
    records = []
    for path in sorted((root / "datasets" / "test-cases").rglob("*.json")):
        data = load_json(path)
        records.append(
            CaseRecord(
                path=path,
                data=data,
                collection=resolve_collection(path, collections),
                schema_errors=validate_case(data, schema),
            )
        )
    return records


def suite_readiness(manifest: dict[str, Any], cases: list[CaseRecord]) -> dict[str, Any]:
    active_by_collection = Counter()
    reviewed_by_collection = Counter()
    pending_by_collection = Counter()

    for case in cases:
        if not case.collection:
            continue
        if case.status == "active":
            active_by_collection[case.collection] += 1
        elif case.status == "reviewed":
            reviewed_by_collection[case.collection] += 1
        elif case.status == "pending_review":
            pending_by_collection[case.collection] += 1

    suites = {}
    for suite_name, suite in manifest.get("suites", {}).items():
        required = suite.get("collections", {})
        missing = {}
        reviewed_waiting = {}
        pending_waiting = {}
        active_total = 0
        required_total = int(suite.get("min_cases", 0))

        for collection, needed in required.items():
            active = active_by_collection[collection]
            active_total += active
            if active < int(needed):
                missing[collection] = int(needed) - active
            if reviewed_by_collection[collection]:
                reviewed_waiting[collection] = reviewed_by_collection[collection]
            if pending_by_collection[collection]:
                pending_waiting[collection] = pending_by_collection[collection]

        if missing:
            state = "blocked"
        elif active_total < required_total:
            state = "blocked"
        else:
            state = "ready"

        suites[suite_name] = {
            "state": state,
            "active_total": active_total,
            "min_cases": required_total,
            "missing_active_cases": missing,
            "reviewed_waiting": reviewed_waiting,
            "pending_review_waiting": pending_waiting,
        }
    return suites


def build_audit(root: Path) -> dict[str, Any]:
    manifest_path = root / "datasets" / "manifest.yaml"
    manifest = load_yaml(manifest_path)
    schema = load_json(root / manifest["schemas"]["test_case"])
    cases = collect_cases(root, manifest, schema)

    status_counts = Counter(case.status for case in cases)
    risk_counts = Counter(case.risk_level for case in cases)
    collection_counts: dict[str, Counter[str]] = defaultdict(Counter)
    schema_failures = []
    orphan_cases = []

    for case in cases:
        if case.collection:
            collection_counts[case.collection][case.status] += 1
        else:
            orphan_cases.append(case.path.relative_to(root).as_posix())
        if case.schema_errors:
            schema_failures.append(
                {
                    "id": case.case_id,
                    "path": case.path.relative_to(root).as_posix(),
                    "errors": case.schema_errors,
                }
            )

    readiness = suite_readiness(manifest, cases)
    blocked_suites = [name for name, data in readiness.items() if data["state"] == "blocked"]
    ready_suites = [name for name, data in readiness.items() if data["state"] == "ready"]
    active_count = status_counts.get("active", 0)

    if not ready_suites:
        maturity = "designed-but-not-operational"
        reason = (
            "The AI QA role structure and manifest are well scoped, but there are not enough "
            "active executable cases to satisfy any declared suite gate."
        )
    elif ready_suites == ["smoke"]:
        maturity = "smoke-operational-foundation"
        reason = (
            "The smoke suite is executable, but release, red_team, model_change, and recurring "
            "regression suites are still underfilled."
        )
    else:
        maturity = "partially-operational"
        reason = (
            "At least one suite is executable, but blocked suites still require dataset backfill "
            "and operational runner coverage."
        )

    top_gaps = []
    if active_count == 0:
        top_gaps.append("No active JSON test cases yet; all executable samples are pending review.")
    elif blocked_suites:
        top_gaps.append(
            f"Only {len(ready_suites)} suite(s) are ready ({', '.join(ready_suites)}); "
            f"{len(blocked_suites)} suite(s) still lack active case inventory."
        )
    if "red_team" in blocked_suites:
        top_gaps.append("Red-team suite is not executable yet; adversarial coverage is still underfilled.")
    if "release" in blocked_suites:
        top_gaps.append("Release suite is not executable yet; capability, hallucination, safety, and injection inventory need backfill.")
    top_gaps.extend(
        [
            "No endpoint runner invokes real model APIs and records latency, token cost, and raw outputs.",
            "No human judge calibration set is available for LLM-as-Judge release decisions.",
            "No production observability import exists for feedback-to-regression promotion.",
        ]
    )

    return {
        "audited_at": datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "manifest_version": manifest.get("version"),
        "dataset_version": manifest.get("dataset_version"),
        "summary": {
            "total_json_cases": len(cases),
            "status_counts": dict(status_counts),
            "risk_counts": dict(risk_counts),
            "schema_failure_count": len(schema_failures),
            "orphan_case_count": len(orphan_cases),
            "ready_suite_count": len(readiness) - len(blocked_suites),
            "blocked_suite_count": len(blocked_suites),
        },
        "collection_counts": {name: dict(counts) for name, counts in sorted(collection_counts.items())},
        "suite_readiness": readiness,
        "schema_failures": schema_failures,
        "orphan_cases": orphan_cases,
        "objective_assessment": {
            "current_maturity": maturity,
            "reason": reason,
            "top_gaps": top_gaps,
        },
    }


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# AI QA Structure Audit",
        "",
        f"- Audited at: `{audit['audited_at']}`",
        f"- Dataset version: `{audit['dataset_version']}`",
        f"- Current maturity: `{audit['objective_assessment']['current_maturity']}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in audit["summary"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Suite Readiness", ""])
    for suite, data in audit["suite_readiness"].items():
        lines.append(
            f"- `{suite}`: `{data['state']}` "
            f"(active `{data['active_total']}` / min `{data['min_cases']}`)"
        )
        if data["missing_active_cases"]:
            missing = ", ".join(f"{k}: {v}" for k, v in data["missing_active_cases"].items())
            lines.append(f"  Missing active cases: {missing}")

    lines.extend(["", "## Top Gaps", ""])
    for gap in audit["objective_assessment"]["top_gaps"]:
        lines.append(f"- {gap}")

    if audit["schema_failures"]:
        lines.extend(["", "## Schema Failures", ""])
        for failure in audit["schema_failures"]:
            lines.append(f"- `{failure['path']}`: {'; '.join(failure['errors'])}")

    lines.extend(
        [
            "",
            "## Professional Upgrade Direction",
            "",
            "1. Promote reviewed adversarial cases to `active` only after safety review.",
            "2. Backfill each manifest collection until smoke and red_team suites are executable.",
            "3. Add a model-runner that writes per-case results under `datasets/results/{model_id}/{dataset_version}/{run_id}/cases/`.",
            "4. Build a 30+ item human calibration set before relying on LLM-as-Judge for release gates.",
            "5. Connect production feedback and incident logs to `datasets/test-cases/feedback/` promotion flow.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit AI QA dataset readiness.")
    parser.add_argument("--json", dest="json_path", help="Write audit JSON to this path.")
    parser.add_argument("--markdown", dest="markdown_path", help="Write audit Markdown to this path.")
    args = parser.parse_args()

    audit = build_audit(ROOT)
    if args.json_path:
        path = ROOT / args.json_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.markdown_path:
        path = ROOT / args.markdown_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown(audit), encoding="utf-8")

    print(json.dumps(audit["summary"], indent=2, ensure_ascii=False))
    return 1 if audit["summary"]["blocked_suite_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
