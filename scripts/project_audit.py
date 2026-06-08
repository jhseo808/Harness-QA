#!/usr/bin/env python3
"""Audit Harness-QA project readiness for QA-team adoption."""

from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import yaml

from ai_qa_audit import build_audit as build_ai_qa_audit
from execute import StepExecutor


ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))


def stamp() -> str:
    return datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S%z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Harness Project Audit",
        "",
        f"- Audited at: `{audit['audited_at']}`",
        f"- Readiness: `{audit['readiness']['level']}`",
        f"- Score: `{audit['readiness']['score']}/100`",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        marker = "PASS" if check["status"] == "pass" else "WARN" if check["status"] == "warn" else "FAIL"
        lines.append(f"- `{marker}` `{check['id']}`: {check['message']}")
        if check.get("details"):
            for detail in check["details"]:
                lines.append(f"  - {detail}")
    lines.extend(["", "## Recommendation", "", audit["readiness"]["recommendation"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def add_check(checks: list[dict[str, Any]], check_id: str, status: str, message: str, details: list[str] | None = None) -> None:
    checks.append({"id": check_id, "status": status, "message": message, "details": details or []})


def audit_json_and_yaml(checks: list[dict[str, Any]]) -> None:
    failures = []
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts or ".pytest_cache" in path.parts:
            continue
        try:
            read_json(path)
        except Exception as exc:  # noqa: BLE001 - audit report should collect failures
            failures.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    for path in sorted(ROOT.rglob("*.yaml")):
        if ".git" in path.parts:
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    add_check(
        checks,
        "json-yaml-parse",
        "fail" if failures else "pass",
        "JSON/YAML files parse cleanly." if not failures else "Some JSON/YAML files failed to parse.",
        failures,
    )


def audit_python(checks: list[dict[str, Any]]) -> None:
    failures = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    add_check(
        checks,
        "python-compile",
        "fail" if failures else "pass",
        "Python scripts compile cleanly." if not failures else "Some Python scripts failed to compile.",
        failures,
    )


def audit_phase_indexes(checks: list[dict[str, Any]]) -> None:
    details = []
    examples_root = ROOT / "examples" / "phases"
    top_index = examples_root / "index.json"
    if top_index.exists():
        top = read_json(top_index)
        indexed = {phase["dir"] for phase in top.get("phases", [])}
        actual = {p.name for p in examples_root.iterdir() if p.is_dir()}
        missing_from_index = sorted(actual - indexed)
        missing_dirs = sorted(indexed - actual)
        if missing_from_index:
            details.append(f"Folders missing from examples/phases/index.json: {', '.join(missing_from_index)}")
        if missing_dirs:
            details.append(f"Indexed folders that do not exist: {', '.join(missing_dirs)}")
    else:
        details.append("examples/phases/index.json is missing.")

    for index_path in sorted((ROOT / "examples" / "phases").glob("*/index.json")):
        phase_dir = index_path.parent
        index = read_json(index_path)
        for step in index.get("steps", []):
            step_file = phase_dir / f"step{step['step']}.md"
            if not step_file.exists():
                details.append(f"{index_path.relative_to(ROOT).as_posix()}: missing {step_file.name}")
            agent = step.get("agent")
            if agent and not (ROOT / "agents" / f"{agent}.md").exists():
                details.append(f"{index_path.relative_to(ROOT).as_posix()}: missing agent {agent}")

    add_check(
        checks,
        "phase-indexes",
        "fail" if details else "pass",
        "Example phase indexes match folders, step files, and agents." if not details else "Example phase indexes have mismatches.",
        details,
    )


def audit_harness_agent_loader(checks: list[dict[str, Any]]) -> None:
    details = []
    examples_root = ROOT / "examples" / "phases"
    for phase_dir in sorted(path for path in examples_root.iterdir() if path.is_dir()):
        index_path = phase_dir / "index.json"
        if not index_path.exists():
            continue
        try:
            executor = StepExecutor(phase_dir.name, phases_dir="examples/phases")
            index = read_json(index_path)
            for step in index.get("steps", []):
                agent = step.get("agent")
                if not agent:
                    continue
                content = executor._load_agent(step)
                if not content.strip():
                    details.append(f"{phase_dir.name} step {step['step']} agent {agent} loaded empty content.")
                    continue
                agent_file = ROOT / "agents" / f"{agent}.md"
                expected_title = agent_file.read_text(encoding="utf-8").splitlines()[0].strip()
                if expected_title and expected_title not in content:
                    details.append(f"{phase_dir.name} step {step['step']} agent {agent} missing agent title in loaded prompt.")
                domain = agent.split("/", 1)[0]
                base_file = ROOT / "agents" / domain / "_base.md"
                if base_file.exists():
                    expected_base = base_file.read_text(encoding="utf-8").splitlines()[0].strip()
                    if expected_base and expected_base not in content:
                        details.append(f"{phase_dir.name} step {step['step']} agent {agent} missing domain base prompt.")
        except Exception as exc:  # noqa: BLE001
            details.append(f"{phase_dir.name}: StepExecutor load failed: {exc}")

    add_check(
        checks,
        "harness-agent-loader",
        "fail" if details else "pass",
        "StepExecutor loads domain base prompts and agent prompts for example phases." if not details else "StepExecutor agent loading has issues.",
        details,
    )


def audit_template_docs(checks: list[dict[str, Any]]) -> None:
    template_files = [
        ROOT / ".claude" / "CLAUDE.md",
        ROOT / "docs" / "PRD.md",
        ROOT / "docs" / "ARCHITECTURE.md",
        ROOT / "docs" / "ADR.md",
    ]
    details = []
    for path in template_files:
        if not path.exists():
            details.append(f"{path.relative_to(ROOT).as_posix()} is missing.")
    add_check(
        checks,
        "template-docs",
        "fail" if details else "pass",
        "Template documentation files exist and are intentionally generic." if not details else "Required template documentation files are missing.",
        details,
    )


def audit_ai_qa(checks: list[dict[str, Any]]) -> None:
    audit = build_ai_qa_audit(ROOT)
    summary = audit["summary"]
    if summary["schema_failure_count"] or summary["orphan_case_count"]:
        status = "fail"
    elif summary["ready_suite_count"] == 0:
        status = "warn"
    else:
        status = "pass"
    details = [
        f"maturity: {audit['objective_assessment']['current_maturity']}",
        f"ready suites: {summary['ready_suite_count']}",
        f"blocked suites: {summary['blocked_suite_count']}",
        f"active cases: {summary['status_counts'].get('active', 0)}",
        f"pending review cases: {summary['status_counts'].get('pending_review', 0)}",
    ]
    add_check(checks, "ai-qa-readiness", status, "AI QA dataset and suite readiness audited.", details)


def audit_command_docs(checks: list[dict[str, Any]]) -> None:
    path = ROOT / ".claude" / "commands" / "harness.md"
    if not path.exists():
        add_check(checks, "command-docs", "fail", "Harness slash command is missing.")
        return
    text = path.read_text(encoding="utf-8")
    required = ["qa/qa-lead", "ai-qa/ai-qa-lead", "ai-qa/ai-evaluator", "ai-qa/ai-safety-tester"]
    missing = [item for item in required if item not in text]
    add_check(
        checks,
        "command-docs",
        "fail" if missing else "pass",
        "Harness slash command lists general QA and AI QA agents." if not missing else "Harness slash command is missing agent entries.",
        missing,
    )


def readiness(checks: list[dict[str, Any]]) -> dict[str, Any]:
    fail_count = sum(1 for check in checks if check["status"] == "fail")
    warn_count = sum(1 for check in checks if check["status"] == "warn")
    score = 100 - fail_count * 20 - warn_count * 8
    score = max(0, score)
    if fail_count:
        level = "not-ready"
        recommendation = "Do not use as a QA-team workflow yet. Fix failing checks first."
    elif warn_count:
        level = "pilot-ready"
        recommendation = (
            "Ready for a controlled QA-team pilot. Fill target-project docs and expand release/red_team "
            "datasets before using it as a hard release gate."
        )
    else:
        level = "team-ready"
        recommendation = "Ready for QA-team use as a standard workflow."
    return {"level": level, "score": score, "recommendation": recommendation}


def build_project_audit() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    audit_json_and_yaml(checks)
    audit_python(checks)
    audit_phase_indexes(checks)
    audit_harness_agent_loader(checks)
    audit_template_docs(checks)
    audit_command_docs(checks)
    audit_ai_qa(checks)
    return {"audited_at": stamp(), "checks": checks, "readiness": readiness(checks)}


def main() -> int:
    audit = build_project_audit()
    write_json(ROOT / "qa-output" / "project-audit.json", audit)
    write_markdown(ROOT / "qa-output" / "project-audit.md", audit)
    print(json.dumps(audit["readiness"], indent=2, ensure_ascii=False))
    return 1 if audit["readiness"]["level"] == "not-ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
