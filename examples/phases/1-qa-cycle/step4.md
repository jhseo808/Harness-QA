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

**CRITICAL: 반드시 아래 순서를 따른다. POM 없이 spec 파일을 작성하지 않는다.**

**작성 순서:**
1. `pages/` 디렉토리 생성 (없는 경우)
2. `pages/TodoPage.ts` 생성 — locator와 action 메서드 정의
3. `tests/todo.spec.ts` 생성 — TodoPage를 import하여 사용

**테스트 대상 플로우:**
1. 할 일 생성 → 목록 표시 확인
2. 상태 전이 (pending → in_progress → done)
3. 할 일 삭제
4. 빈 입력 제출 시 에러 메시지

**POM 구조 예시:**
```typescript
// pages/TodoPage.ts
export class TodoPage {
  constructor(private page: Page) {}

  // Locators
  readonly inputField = this.page.getByRole('textbox', { name: '할 일 입력' });
  readonly submitButton = this.page.getByRole('button', { name: '추가' });

  // Actions
  async goto() { await this.page.goto('/'); }
  async addTodo(text: string) {
    await this.inputField.fill(text);
    await this.submitButton.click();
  }
}

// tests/todo.spec.ts
import { TodoPage } from '../pages/TodoPage';
test.beforeEach(async ({ page }) => {
  todoPage = new TodoPage(page);
  await todoPage.goto();
});
```

## Acceptance Criteria

```bash
npx playwright test --reporter=list
# 모든 케이스 실행 완료 (일부 실패 있어도 실행은 완료해야 함)
```

`qa-output/playwright-result.md` 작성 완료

`pages/TodoPage.ts` 존재 확인 — 이 파일이 없으면 작업 미완료

## 검증 절차

1. Acceptance Criteria를 모두 충족했는지 확인한다.
2. 작업 완료 후 `examples/phases/1-qa-cycle/step4-result.json`을 작성하라:
   - 완료 → `{"status": "completed", "summary": "Playwright 테스트 N개 실행. 통과: N, 실패: N. 결함 N건 발견.", "artifacts": ["qa-output/playwright-result.md", "qa-output/playwright-summary.json", "tests/todo.spec.ts", "pages/TodoPage.ts"]}`
   - 환경 문제 → `{"status": "blocked", "blocked_reason": "앱 서버 미실행 또는 playwright 미설치"}`

## 금지사항

- POM(Page Object Model) 없이 spec 파일을 작성하지 마라. 이유: 로케이터 중복 및 유지보수성 저하.
- API 엔드포인트를 직접 호출해 테스트하지 마라. 이유: API 검증은 step 3에서 완료.
