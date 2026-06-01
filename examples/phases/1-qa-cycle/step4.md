# Step 4: web-ui-testing (Playwright)

## 컨텍스트

이전 step 산출물을 먼저 읽어라:
- `qa-output/test-cases.md` — playwright에 배정된 케이스 ID 목록
- `qa-output/test-strategy.md` — 테스트 대상 사용자 플로우
- `qa-output/api-test-result.md` — API 테스트에서 발견된 결함 참조 (UI 관련 영향 확인)

테스트 환경:
- URL: `http://localhost:3000`
- 브라우저: Chromium (기본)

## 작업

배정된 케이스를 기반으로 E2E 테스트를 작성하고 실행하라.

**테스트 대상 플로우:**
1. 할 일 생성 → 목록 표시 확인
2. 상태 전이 (pending → in_progress → done)
3. 할 일 삭제
4. 빈 입력 제출 시 에러 메시지

## Acceptance Criteria

```bash
npx playwright test --reporter=list
# 모든 케이스 실행 완료 (일부 실패 있어도 실행은 완료해야 함)
```

`qa-output/playwright-result.md` 작성 완료

## 결과 파일 작성

`examples/phases/1-qa-cycle/step4-result.json`:
- 완료 → `{"status": "completed", "summary": "Playwright 테스트 N개 실행. 통과: N, 실패: N. 결함 N건 발견.", "artifacts": ["qa-output/playwright-result.md", "qa-output/playwright-summary.json", "tests/todo.spec.ts", "pages/TodoPage.ts"]}`
- 환경 문제 → `{"status": "blocked", "blocked_reason": "앱 서버 미실행 또는 playwright 미설치"}`
