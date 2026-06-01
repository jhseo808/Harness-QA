# Harness-QA 상태 요약

> 컨텍스트 압축 후 재진입 시 이 파일을 먼저 읽어라.

---

## 프로젝트 개요

**목적**: QA 팀처럼 움직이는 AI agent 기반 QA 하네스 엔지니어링 구조 만들기.  
테스트 커버리지나 test_execute.py 유지보수가 목적이 아님.

**핵심 파일 구조**:
```
agents/qa/          ← QA agent 프롬프트 파일들
  _base.md          ← 팀 공통 규약, 결함 분류, 산출물 경로 규약, Step 상태 기준
  qa-lead.md        ← QA 전략 수립, agent 선택, 품질 게이트 정의
  requirements-analyst.md
  test-case-designer.md
  playwright.md
  appium.md
  api-tester.md
  ai-service-tester.md
  performance-tester.md
  security-tester.md
  reporter.md
scripts/execute.py  ← 하네스 실행기 (phase 내 step 순차 실행)
phases/             ← 실제 실행할 phase (index.json + step*.md)
examples/phases/    ← 예제 phase (--phases-dir examples/phases 로 실행)
```

**실행 방법**:
```bash
python scripts/execute.py <phase-dir>
python scripts/execute.py <phase-dir> --phases-dir examples/phases   # 예제 실행
python scripts/execute.py <phase-dir> --push                         # 완료 후 push
```

---

## 현재 상태 (2026-06-01 기준, 점수 97/100)

### 완성된 구조
- **execute.py**: step-result.json 계약, MAX_RETRIES=3, blocked/error 분기, qa-output/ 자동 생성
- **_base.md**: 108줄 (lean) — 결함 분류, 테스트 ID, 산출물 형식, 경로 규약, Step 상태 기준, 품질 게이트
- **모든 agent**: qa-lead 전략 문서(`qa-output/qa-strategy.md`) 참조 추가 완료 (10/10)
- **산출물 경로**: 모든 agent가 `qa-output/` 아래 표준 경로로 통일
- **예제**: `examples/phases/0-mvp/` (5 steps), `examples/phases/1-qa-cycle/` (6 steps)

### step-result.json 스키마
```json
{"status": "completed", "summary": "한 줄 요약", "artifacts": ["qa-output/test-strategy.md"]}
{"status": "error", "error_message": "실패 원인"}
{"status": "blocked", "blocked_reason": "이유"}
```
executor가 이 파일을 읽어 index.json을 갱신한다. Claude가 index.json을 직접 수정하면 안 된다.

### 산출물 경로 규약
| Agent | 산출물 파일 |
|-------|-----------|
| qa-lead | `qa-output/qa-strategy.md` |
| requirements-analyst | `qa-output/test-strategy.md` |
| test-case-designer | `qa-output/test-cases.md`, `qa-output/coverage-matrix.md` |
| playwright | `qa-output/playwright-result.md`, `qa-output/playwright-summary.json` |
| appium | `qa-output/appium-result.md`, `qa-output/appium-summary.json` |
| api-tester | `qa-output/api-test-result.md`, `qa-output/api-test-summary.json` |
| ai-service-tester | `qa-output/ai-test-result.md`, `qa-output/ai-test-summary.json` |
| performance-tester | `qa-output/performance-result.md`, `qa-output/performance-summary.json` |
| security-tester | `qa-output/security-result.md`, `qa-output/security-summary.json` |
| reporter | `qa-output/release-report.md` |

---

## 잔여 TODO (선택적 개선)

### 97점 → 100점을 위한 나머지 3점

| 항목 | 이유 | 우선순위 |
|------|------|---------|
| `guardrails`에서 docs/*.md 로드를 opt-in으로 변경 | 현재 docs/ 폴더가 비어 있어 무해하지만, 파일이 생기면 매 step 누적 | 낮음 |
| `claude --output-format json` 파싱 실패 시 fallback | stdout 파싱 오류가 result 미생성으로 처리되긴 하지만 에러 메시지 부정확 | 낮음 |
| `phases/` 디렉토리 신규 phase 생성 템플릿 | 예제가 my-todo-app에 의존적, 범용 템플릿 없음 | 낮음 |
