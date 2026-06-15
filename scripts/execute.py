#!/usr/bin/env python3
"""
Harness Step Executor — phase 내 step을 순차 실행하고 자가 교정한다.

Usage:
    python3 scripts/execute.py <phase-dir> [--phases-dir <dir>] [--push]
"""

import argparse
import contextlib
import json
import os
import subprocess
import sys
import threading
import time
import types
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

# step{N}-result.json 스키마:
# completed: {"status": "completed", "summary": "...", "artifacts": ["path", ...]}
# error:     {"status": "error", "error_message": "..."}
# blocked:   {"status": "blocked", "blocked_reason": "..."}


@contextlib.contextmanager
def progress_indicator(label: str):
    """터미널 진행 표시기. with 문으로 사용하며 .elapsed 로 경과 시간을 읽는다."""
    frames = "◐◓◑◒"
    stop = threading.Event()
    t0 = time.monotonic()

    def _animate():
        idx = 0
        while not stop.wait(0.12):
            sec = int(time.monotonic() - t0)
            sys.stderr.write(f"\r{frames[idx % len(frames)]} {label} [{sec}s]")
            sys.stderr.flush()
            idx += 1
        sys.stderr.write("\r" + " " * (len(label) + 20) + "\r")
        sys.stderr.flush()

    th = threading.Thread(target=_animate, daemon=True)
    th.start()
    info = types.SimpleNamespace(elapsed=0.0)
    try:
        yield info
    finally:
        stop.set()
        th.join()
        info.elapsed = time.monotonic() - t0


class StepExecutor:
    """Phase 디렉토리 안의 step들을 순차 실행하는 하네스."""

    MAX_RETRIES = 3
    FEAT_MSG = "feat({phase}): step {num} — {name}"
    CHORE_MSG = "chore({phase}): step {num} output"
    TZ = timezone(timedelta(hours=9))

    def __init__(self, phase_dir_name: str, *, phases_dir: str = "phases", auto_push: bool = False, skip_permissions: bool = True):
        self._root = str(ROOT)
        self._phases_dir = ROOT / phases_dir
        self._phase_dir = self._phases_dir / phase_dir_name
        self._skip_permissions = skip_permissions
        self._phase_dir_name = phase_dir_name
        self._top_index_file = self._phases_dir / "index.json"
        self._auto_push = auto_push

        if not self._phase_dir.is_dir():
            print(f"ERROR: {self._phase_dir} not found")
            sys.exit(1)

        self._index_file = self._phase_dir / "index.json"
        if not self._index_file.exists():
            print(f"ERROR: {self._index_file} not found")
            sys.exit(1)

        idx = self._read_json(self._index_file)
        self._project = idx.get("project", "project")
        self._phase_name = idx.get("phase", phase_dir_name)
        self._total = len(idx["steps"])

    def run(self):
        self._print_header()
        self._check_blockers()
        self._check_clean_tree()
        self._checkout_branch()
        guardrails = self._load_guardrails()
        self._ensure_created_at()
        self._execute_all_steps(guardrails)
        self._finalize()

    # --- timestamps ---

    def _stamp(self) -> str:
        return datetime.now(self.TZ).strftime("%Y-%m-%dT%H:%M:%S%z")

    # --- JSON I/O ---

    @staticmethod
    def _read_json(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(p: Path, data: dict):
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- git ---

    def _run_git(self, *args) -> subprocess.CompletedProcess:
        cmd = ["git"] + list(args)
        return subprocess.run(cmd, cwd=self._root, capture_output=True, text=True)

    def _check_clean_tree(self):
        """phase 디렉토리 외부에 uncommitted 변경이 없는지 확인한다.
        phase spec 파일(step*.md, index.json)은 커밋 전 상태여도 허용한다."""
        r = self._run_git("status", "--porcelain")
        if r.returncode != 0:
            return  # git 사용 불가는 _checkout_branch에서 처리
        if not r.stdout.strip():
            return
        phase_prefix = self._phase_dir.relative_to(ROOT).as_posix()
        dirty_outside = []
        for line in r.stdout.splitlines():
            if not line.strip():
                continue
            # porcelain 형식: "XY path" (rename은 "XY old -> new" — 마지막 경로를 사용)
            filepath = line[3:].split(" -> ")[-1].strip().strip('"')
            if not filepath.startswith(phase_prefix):
                dirty_outside.append(line)
        if dirty_outside:
            print(f"\n  ERROR: phase 디렉토리 외부에 uncommitted 변경이 있습니다.")
            print(f"  하네스가 자동 커밋하면 기존 변경과 뒤섞입니다.")
            print(f"  실행 전에 변경사항을 commit 또는 stash하세요:\n")
            print("\n".join(dirty_outside[:20]))
            sys.exit(1)

    def _checkout_branch(self):
        branch = f"feat-{self._phase_name}"

        r = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        if r.returncode != 0:
            print(f"  ERROR: git을 사용할 수 없거나 git repo가 아닙니다.")
            print(f"  {r.stderr.strip()}")
            sys.exit(1)

        if r.stdout.strip() == branch:
            return

        r = self._run_git("rev-parse", "--verify", branch)
        r = self._run_git("checkout", branch) if r.returncode == 0 else self._run_git("checkout", "-b", branch)

        if r.returncode != 0:
            print(f"  ERROR: 브랜치 '{branch}' checkout 실패.")
            print(f"  {r.stderr.strip()}")
            print(f"  Hint: 변경사항을 stash하거나 commit한 후 다시 시도하세요.")
            sys.exit(1)

        print(f"  Branch: {branch}")

    def _commit_step(self, step_num: int, step_name: str):
        # 하네스 산출물 파일(output, result)은 코드 커밋에서 제외
        phase_rel = self._phase_dir.relative_to(Path(self._root)).as_posix()
        output_rel = f"{phase_rel}/step{step_num}-output.json"
        result_rel = f"{phase_rel}/step{step_num}-result.json"
        index_rel = f"{phase_rel}/index.json"

        self._run_git("add", "-A")
        self._run_git("reset", "HEAD", "--", output_rel)  # output은 두 커밋 모두에서 제외
        self._run_git("reset", "HEAD", "--", result_rel)
        self._run_git("reset", "HEAD", "--", index_rel)
        self._run_git("reset", "HEAD", "--", "qa-output")

        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = self.FEAT_MSG.format(phase=self._phase_name, num=step_num, name=step_name)
            r = self._run_git("commit", "-m", msg)
            if r.returncode == 0:
                print(f"  Commit: {msg}")
            else:
                print(f"  WARN: 코드 커밋 실패: {r.stderr.strip()}")

        # 2차 커밋: result.json, index.json 등 하네스 추적 파일만 포함.
        # 1차 커밋(코드)에서 제외했던 파일들이 다시 add됨 — 의도된 2-commit 전략.
        # output.json만 여전히 제외(step 원시 로그는 영구 보관 불필요).
        self._run_git("add", "-A")
        self._run_git("reset", "HEAD", "--", output_rel)  # output은 커밋하지 않음
        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = self.CHORE_MSG.format(phase=self._phase_name, num=step_num)
            r = self._run_git("commit", "-m", msg)
            if r.returncode != 0:
                print(f"  WARN: housekeeping 커밋 실패: {r.stderr.strip()}")

    # --- top-level index ---

    def _update_top_index(self, status: str):
        if not self._top_index_file.exists():
            return
        top = self._read_json(self._top_index_file)
        ts = self._stamp()
        for phase in top.get("phases", []):
            if phase.get("dir") == self._phase_dir_name:
                phase["status"] = status
                ts_key = {"completed": "completed_at", "error": "failed_at", "blocked": "blocked_at"}.get(status)
                if ts_key:
                    phase[ts_key] = ts
                break
        self._write_json(self._top_index_file, top)

    # --- guardrails & context ---

    def _load_guardrails(self) -> str:
        sections = []
        claude_md = ROOT / "CLAUDE.md"
        if claude_md.exists():
            sections.append(f"## 프로젝트 규칙 (CLAUDE.md)\n\n{claude_md.read_text(encoding='utf-8')}")
        project_claude_md = ROOT / ".claude" / "CLAUDE.md"
        if project_claude_md.exists():
            sections.append(f"## 프로젝트별 지침 (.claude/CLAUDE.md)\n\n{project_claude_md.read_text(encoding='utf-8')}")
        docs_dir = ROOT / "docs"
        if docs_dir.is_dir():
            for doc in sorted(docs_dir.glob("*.md")):
                sections.append(f"## {doc.stem}\n\n{doc.read_text(encoding='utf-8')}")
        return "\n\n---\n\n".join(sections) if sections else ""

    def _load_agent(self, step: dict) -> str:
        """agent 프롬프트를 로드한다. agent가 지정됐는데 파일이 없으면 즉시 종료한다."""
        agent_path = step.get("agent", "")
        if not agent_path:
            return ""
        sections = []
        domain = str(Path(agent_path).parent)
        base_file = ROOT / "agents" / domain / "_base.md"
        if base_file.exists():
            sections.append(base_file.read_text(encoding="utf-8"))
        agent_file = ROOT / "agents" / f"{agent_path}.md"
        if not agent_file.exists():
            print(f"  ERROR: agent '{agent_path}' 파일을 찾을 수 없습니다.")
            print(f"  경로: {agent_file}")
            print(f"  Hint: index.json의 \"agent\" 값을 확인하세요 (오타 여부, agents/ 기준 상대경로).")
            sys.exit(1)
        sections.append(agent_file.read_text(encoding="utf-8"))
        return "\n\n---\n\n".join(sections)

    @staticmethod
    def _build_step_context(index: dict) -> str:
        lines = []
        for s in index["steps"]:
            if s["status"] == "completed" and s.get("summary"):
                line = f"- Step {s['step']} ({s['name']}): {s['summary']}"
                if s.get("artifacts"):
                    line += f"\n  생성된 산출물: {', '.join(s['artifacts'])}"
                lines.append(line)
        if not lines:
            return ""
        return "## 이전 Step 산출물\n\n" + "\n".join(lines) + "\n\n"

    def _build_preamble(self, step_num: int, guardrails: str, step_context: str,
                        agent_content: str = "", prev_error: Optional[str] = None) -> str:
        result_path = (self._phase_dir / f"step{step_num}-result.json").relative_to(Path(self._root)).as_posix()
        retry_section = ""
        if prev_error:
            retry_section = (
                f"\n## ⚠ 이전 시도 실패 — 아래 에러를 반드시 참고하여 수정하라\n\n"
                f"{prev_error}\n\n---\n\n"
            )
        agent_section = f"\n\n---\n\n{agent_content}" if agent_content else ""
        return (
            f"당신은 {self._project} 프로젝트의 QA 팀원입니다. 아래 step을 수행하세요.\n\n"
            f"{guardrails}{agent_section}\n\n---\n\n"
            f"{step_context}{retry_section}"
            f"## 작업 규칙\n\n"
            f"1. 이전 step에서 작성된 코드를 확인하고 일관성을 유지하라.\n"
            f"2. 이 step에 명시된 작업만 수행하라. 추가 기능이나 파일을 만들지 마라.\n"
            f"3. 기존 테스트를 깨뜨리지 마라.\n"
            f"4. AC(Acceptance Criteria) 검증을 직접 실행하라.\n"
            f"5. 산출물 파일을 `qa-output/` 디렉토리에 작성하라. 디렉토리가 없으면 먼저 생성하라.\n"
            f"6. 작업 완료 후 반드시 `{result_path}` 파일을 아래 형식으로 작성하라.\n"
            f"   index.json은 수정하지 말 것 — 하네스가 직접 업데이트한다.\n\n"
            f"   AC 통과 시: {{\"status\": \"completed\", \"summary\": \"<한 줄 요약>\", \"artifacts\": [\"<파일 경로>\", ...]}}\n"
            f"   실패 시: {{\"status\": \"error\", \"error_message\": \"<원인>\"}}\n"
            f"   개입 필요 시: {{\"status\": \"blocked\", \"blocked_reason\": \"<이유>\"}}\n\n---\n\n"
        )

    # --- step 결과 파싱 ---

    @staticmethod
    def _validate_step_result(data: dict) -> Optional[str]:
        """result dict를 검증한다. 문제가 있으면 에러 메시지를 반환, 없으면 None."""
        status = data.get("status")
        if status not in ("completed", "error", "blocked"):
            return f"status는 completed/error/blocked 중 하나여야 함 (받은 값: {status!r})"
        if status == "completed":
            if not data.get("summary", "").strip():
                return "completed 시 summary 필드는 비어있을 수 없음"
            artifacts = data.get("artifacts")
            if artifacts is not None and not isinstance(artifacts, list):
                return f"artifacts는 list여야 함 (받은 타입: {type(artifacts).__name__})"
        elif status == "error":
            if not data.get("error_message", "").strip():
                return "error 시 error_message 필드는 비어있을 수 없음"
        elif status == "blocked":
            if not data.get("blocked_reason", "").strip():
                return "blocked 시 blocked_reason 필드는 비어있을 수 없음"
        return None

    def _read_step_result(self, step_num: int) -> dict:
        """step{N}-result.json을 읽고 검증한다. 없거나 유효하지 않으면 status=pending 반환."""
        result_file = self._phase_dir / f"step{step_num}-result.json"
        if not result_file.exists():
            return {"status": "pending", "_parse_error": "result 파일 없음"}
        try:
            data = self._read_json(result_file)
        except json.JSONDecodeError as e:
            return {"status": "pending", "_parse_error": f"JSON 파싱 실패: {e}"}
        err = self._validate_step_result(data)
        if err:
            return {"status": "pending", "_parse_error": err}
        return data

    def _apply_step_result(self, step_num: int, result: dict, ts: str):
        """result 내용을 index.json의 해당 step에 반영한다."""
        index = self._read_json(self._index_file)
        status = result["status"]
        for s in index["steps"]:
            if s["step"] != step_num:
                continue
            for stale in ("summary", "completed_at", "artifacts",
                          "error_message", "failed_at",
                          "blocked_reason", "blocked_at"):
                s.pop(stale, None)
            s["status"] = status
            if status == "completed":
                s["summary"] = result.get("summary", "")
                s["completed_at"] = ts
                if result.get("artifacts"):
                    s["artifacts"] = result["artifacts"]
            elif status == "error":
                s["error_message"] = result.get("error_message", "unknown error")
                s["failed_at"] = ts
            elif status == "blocked":
                s["blocked_reason"] = result.get("blocked_reason", "unknown")
                s["blocked_at"] = ts
            break
        self._write_json(self._index_file, index)

    # --- Claude 호출 ---

    def _build_runner_cmd(self, prompt: str) -> list:
        """AI runner 호출 명령을 조립한다. 모델/도구 교체 시 이 메서드만 수정한다."""
        cmd = ["claude", "-p"]
        if self._skip_permissions:
            cmd += ["--dangerously-skip-permissions"]
        return cmd + ["--output-format", "json", prompt]

    def _invoke_claude(self, step: dict, preamble: str) -> dict:
        step_num, step_name = step["step"], step["name"]
        step_file = self._phase_dir / f"step{step_num}.md"

        if not step_file.exists():
            print(f"  ERROR: {step_file} not found")
            sys.exit(1)

        prompt = preamble + step_file.read_text(encoding="utf-8")
        result = subprocess.run(
            self._build_runner_cmd(prompt),
            cwd=self._root, capture_output=True, text=True, timeout=1800,
        )

        if result.returncode != 0:
            print(f"\n  WARN: Claude가 비정상 종료됨 (code {result.returncode})")
            if result.stderr:
                print(f"  stderr: {result.stderr[:500]}")

        output = {
            "step": step_num, "name": step_name,
            "exitCode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
        }
        out_path = self._phase_dir / f"step{step_num}-output.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return output

    # --- 헤더 & 검증 ---

    def _print_header(self):
        print(f"\n{'='*60}")
        print(f"  Harness Step Executor")
        print(f"  Phase: {self._phase_name} | Steps: {self._total}")
        if self._auto_push:
            print(f"  Auto-push: enabled")
        print(f"{'='*60}")

    def _check_blockers(self):
        index = self._read_json(self._index_file)
        for s in index["steps"]:
            if s["status"] == "error":
                print(f"\n  ✗ Step {s['step']} ({s['name']}) failed.")
                print(f"  Error: {s.get('error_message', 'unknown')}")
                print(f"  Fix and reset status to 'pending' to retry.")
                sys.exit(1)
            if s["status"] == "blocked":
                print(f"\n  ⏸ Step {s['step']} ({s['name']}) blocked.")
                print(f"  Reason: {s.get('blocked_reason', 'unknown')}")
                print(f"  Resolve and reset status to 'pending' to retry.")
                sys.exit(2)
            if s["status"] == "pending":
                break

    def _ensure_created_at(self):
        index = self._read_json(self._index_file)
        if "created_at" not in index:
            index["created_at"] = self._stamp()
            self._write_json(self._index_file, index)

    # --- 실행 루프 ---

    def _execute_single_step(self, step: dict, guardrails: str) -> bool:
        """단일 step 실행 (재시도 포함). 완료되면 True, 실패/차단이면 False."""
        step_num, step_name = step["step"], step["name"]
        done = sum(1 for s in self._read_json(self._index_file)["steps"] if s["status"] == "completed")
        prev_error = None
        agent_content = self._load_agent(step)
        (Path(self._root) / "qa-output").mkdir(exist_ok=True)

        for attempt in range(1, self.MAX_RETRIES + 1):
            # 중단 후 재시작 복구: 유효한 completed/blocked result가 이미 있으면 Claude 재호출 없이 사용
            existing = self._read_step_result(step_num)
            if existing["status"] in ("completed", "blocked"):
                result = existing
                ts = self._stamp()
                if result["status"] == "completed":
                    self._apply_step_result(step_num, result, ts)
                    self._commit_step(step_num, step_name)
                    print(f"  ✓ Step {step_num}: {step_name} [recovered from previous run]")
                    if result.get("artifacts"):
                        print(f"    산출물: {', '.join(result['artifacts'])}")
                    return True
                else:
                    self._apply_step_result(step_num, result, ts)
                    reason = result.get("blocked_reason", "")
                    print(f"  ⏸ Step {step_num}: {step_name} blocked [recovered]")
                    print(f"    Reason: {reason}")
                    self._update_top_index("blocked")
                    sys.exit(2)

            # 이전 실패 result를 삭제하고 Claude 재호출
            (self._phase_dir / f"step{step_num}-result.json").unlink(missing_ok=True)

            index = self._read_json(self._index_file)
            step_context = self._build_step_context(index)
            preamble = self._build_preamble(step_num, guardrails, step_context, agent_content, prev_error)

            tag = f"Step {step_num}/{self._total - 1} ({done} done): {step_name}"
            if attempt > 1:
                tag += f" [retry {attempt}/{self.MAX_RETRIES}]"

            with progress_indicator(tag) as pi:
                self._invoke_claude(step, preamble)
                elapsed = int(pi.elapsed)

            result = self._read_step_result(step_num)
            status = result["status"]
            ts = self._stamp()

            if status == "completed":
                self._apply_step_result(step_num, result, ts)
                self._commit_step(step_num, step_name)
                print(f"  ✓ Step {step_num}: {step_name} [{elapsed}s]")
                if result.get("artifacts"):
                    print(f"    산출물: {', '.join(result['artifacts'])}")
                return True

            if status == "blocked":
                self._apply_step_result(step_num, result, ts)
                reason = result.get("blocked_reason", "")
                print(f"  ⏸ Step {step_num}: {step_name} blocked [{elapsed}s]")
                print(f"    Reason: {reason}")
                self._update_top_index("blocked")
                sys.exit(2)

            # pending(result 파일 미생성 포함) 또는 error
            err_msg = result.get("error_message") or result.get("_parse_error") or "result 파일 미생성 또는 status 누락"

            if attempt < self.MAX_RETRIES:
                prev_error = err_msg
                print(f"  ↻ Step {step_num}: retry {attempt}/{self.MAX_RETRIES} — {err_msg}")
            else:
                final_err = f"[{self.MAX_RETRIES}회 시도 후 실패] {err_msg}"
                self._apply_step_result(step_num, {"status": "error", "error_message": final_err}, ts)
                self._commit_step(step_num, step_name)
                print(f"  ✗ Step {step_num}: {step_name} failed after {self.MAX_RETRIES} attempts [{elapsed}s]")
                print(f"    Error: {final_err}")
                self._update_top_index("error")
                sys.exit(1)

        return False  # unreachable

    def _execute_all_steps(self, guardrails: str):
        while True:
            index = self._read_json(self._index_file)
            pending = next((s for s in index["steps"] if s["status"] == "pending"), None)
            if pending is None:
                print("\n  All steps completed!")
                return

            step_num = pending["step"]
            for s in index["steps"]:
                if s["step"] == step_num and "started_at" not in s:
                    s["started_at"] = self._stamp()
                    self._write_json(self._index_file, index)
                    break

            self._execute_single_step(pending, guardrails)

    def _finalize(self):
        index = self._read_json(self._index_file)
        index["completed_at"] = self._stamp()
        self._write_json(self._index_file, index)
        self._update_top_index("completed")

        self._run_git("add", "-A")
        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = f"chore({self._phase_name}): mark phase completed"
            r = self._run_git("commit", "-m", msg)
            if r.returncode == 0:
                print(f"  ✓ {msg}")

        if self._auto_push:
            branch = f"feat-{self._phase_name}"
            r = self._run_git("push", "-u", "origin", branch)
            if r.returncode != 0:
                print(f"\n  ERROR: git push 실패: {r.stderr.strip()}")
                sys.exit(1)
            print(f"  ✓ Pushed to origin/{branch}")

        print(f"\n{'='*60}")
        print(f"  Phase '{self._phase_name}' completed!")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Harness Step Executor")
    parser.add_argument("phase_dir", help="Phase directory name (e.g. 0-mvp)")
    parser.add_argument("--phases-dir", default="phases",
                        help="Phases root directory relative to project root (default: phases). "
                             "Use 'examples/phases' to run example phases.")
    parser.add_argument("--push", action="store_true", help="Push branch after completion")
    parser.add_argument("--no-skip-permissions", action="store_true",
                        help="Do not pass --dangerously-skip-permissions to Claude CLI")
    args = parser.parse_args()

    StepExecutor(
        args.phase_dir,
        phases_dir=args.phases_dir,
        auto_push=args.push,
        skip_permissions=not args.no_skip_permissions,
    ).run()


if __name__ == "__main__":
    main()
