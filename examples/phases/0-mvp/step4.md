# Step 4: qa-web

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/CLAUDE.md`
- `phases/0-mvp/index.json` (이전 step 완료 현황 및 summary 확인)
- `app/` 하위 페이지 컴포넌트 전체
- `app/api/` 하위 API 라우트 전체

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

Todo 앱의 핵심 사용자 시나리오에 대한 E2E 테스트를 작성하고 실행하라.

### 테스트 대상 기능

1. **할 일 생성**: 입력 → 제출 → 목록에 표시 확인
2. **상태 변경**: pending → in_progress → done 전환
3. **할 일 삭제**: 삭제 버튼 클릭 → 목록에서 제거 확인
4. **빈 입력 방지**: 빈 제목 제출 시 에러 메시지 노출 확인

### 파일 구조 계약

```
testcase/todo-create.md      # 생성 기능 테스트케이스 문서
testcase/todo-status.md      # 상태 변경 테스트케이스 문서
tests/todo-create.spec.ts    # Playwright 테스트 코드
tests/todo-status.spec.ts    # Playwright 테스트 코드
pages/TodoPage.ts            # Page Object Model
reports/                     # 테스트 결과 (실행 후 자동 생성)
```

### POM 시그니처

```typescript
// pages/TodoPage.ts
export class TodoPage {
  constructor(private page: Page) {}

  async navigate(): Promise<void>
  async createTodo(title: string): Promise<void>
  async changeStatus(todoId: string, status: TodoStatus): Promise<void>
  async deleteTodo(todoId: string): Promise<void>
  async getTodoCount(): Promise<number>
}
```

## Acceptance Criteria

```bash
npx playwright test --reporter=html
# 결과: 모든 테스트 통과, reports/index.html 생성
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - testcase/, tests/, pages/, reports/ 4개 디렉토리가 모두 존재하는가?
   - POM이 Page 클래스 형태로 캡슐화되어 있는가?
   - 로케이터가 `getByRole()` 우선으로 작성되었는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 step 4를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "E2E 테스트 N개 통과. todo-create, todo-status 시나리오 검증 완료. reports/index.html 생성."`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 앱 서버 미실행 등 환경 문제 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"`

## 금지사항

- `locator('input[type=checkbox]')` 같은 CSS 셀렉터를 1순위로 쓰지 마라. 이유: DOM 구조 변경 시 깨지기 쉽다. `getByRole('checkbox', { name: '...' })`를 먼저 시도하라.
- `page.waitForTimeout(N)`으로 고정 대기하지 마라. 이유: 환경마다 타이밍이 달라 불안정한 테스트(flaky)가 된다. `waitForSelector` 또는 `expect(locator).toBeVisible()`로 대체하라.
- `auth.json`을 커밋하지 마라. 이유: 세션 토큰이 포함되어 보안 위협이 된다.
- 기존 테스트를 깨뜨리지 마라.
