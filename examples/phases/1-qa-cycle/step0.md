# Step 0: qa-strategy (QA Lead)

## 컨텍스트

이번 QA 사이클 대상: **my-todo-app MVP 릴리스 후보**

**변경 범위:**
- Todo CRUD API (GET/POST/PATCH/DELETE `/api/todos`)
- TodoItem, TodoList, TodoForm 웹 UI 컴포넌트
- 신규 기능: 상태 전이 (pending → in_progress → done)
- 인증 없음 (MVP 범위), 개인정보 처리 없음

**릴리스 제약:**
- 릴리스 목표일: D+5
- 성능 SLA: 없음 (MVP)
- 보안 요건: 없음 (인증 없는 내부 앱)

**환경:**
- Staging URL: `http://localhost:3000` (로컬 개발 서버)
- API 테스트 계정: 불필요 (인증 없음)

## 작업

위 정보를 바탕으로 이번 QA 사이클의 전략을 수립하고 `qa-output/qa-strategy.md`를 작성하라.
phase step 구성(index.json)은 이미 확정됐으므로 별도 계획 파일은 작성하지 않는다.

## Acceptance Criteria

- `qa-output/qa-strategy.md` 파일이 존재하고 다음을 포함:
  - 활성화 agent 목록 및 이유 (playwright, api-tester는 필수, 나머지는 제외 이유 명시)
  - 이번 사이클 품질 게이트
  - 환경 선행 조건 체크리스트

## 검증 절차

1. Acceptance Criteria를 모두 충족했는지 확인한다.
2. 작업 완료 후 `examples/phases/1-qa-cycle/step0-result.json`을 작성하라
   (index.json은 하네스가 자동 갱신 — 직접 수정 금지):
   - 성공 → `{"status": "completed", "summary": "QA 전략 수립 완료. 활성화 agent: requirements-analyst, test-case-designer, api-tester, playwright, reporter", "artifacts": ["qa-output/qa-strategy.md"]}`
   - 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`

## 금지사항

- 이번 step에서 테스트 케이스나 테스트 코드를 작성하지 마라. 이유: 전략 수립만 담당하며, 케이스 설계는 step 2에서 수행.
- index.json을 직접 수정하지 마라. 이유: 하네스가 자동 관리하는 파일.
