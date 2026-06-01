# Step 1: requirements-analysis (Requirements Analyst)

## 컨텍스트

이전 step 산출물을 먼저 읽어라:
- `qa-output/qa-strategy.md` — 활성화된 agent, 품질 게이트, 범위 제약 확인

분석 대상 소스 파일:
- `app/api/todos/route.ts` (GET/POST)
- `app/api/todos/[id]/route.ts` (PATCH/DELETE)
- `components/TodoItem.tsx`, `components/TodoList.tsx`, `components/TodoForm.tsx`
- `app/page.tsx`
- `types/todo.ts`, `types/todo.schema.ts`

## 작업

위 소스 파일을 읽고 요구사항을 분석하여 `qa-output/test-strategy.md`를 작성하라.
qa-strategy.md의 활성화 agent 목록을 반드시 확인하고 그 범위 내에서만 분석하라.

## Acceptance Criteria

`qa-output/test-strategy.md`에 다음이 포함되어야 한다:
- 테스트 범위 (포함/제외 항목)
- 각 API 엔드포인트 + UI 기능의 수용 기준 (Gherkin 형식)
- 통합 접점 목록 (API ↔ UI 경계)
- 리스크 분석 (P0/P1 우선순위)
- 요구사항 GAP 목록 (모호한 부분)

## 결과 파일 작성

`examples/phases/1-qa-cycle/step1-result.json`:
- 성공 → `{"status": "completed", "summary": "요구사항 분석 완료. AC N개 작성. GAP N건 발견.", "artifacts": ["qa-output/test-strategy.md"]}`
- 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`
