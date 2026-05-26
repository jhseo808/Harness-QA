# Step 3: ui-components

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/CLAUDE.md`
- `types/todo.ts` (step 1 산출물)
- `app/api/todos/route.ts`, `app/api/todos/[id]/route.ts` (step 2 산출물)
- `app/page.tsx` (step 0 산출물 — 현재 빈 홈 페이지)

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

Todo 앱의 핵심 UI 컴포넌트를 구현하라.

### 생성할 파일

```
components/
├── TodoList.tsx       # Todo 목록 렌더링
├── TodoItem.tsx       # 단일 Todo 항목 (체크박스, 제목, 삭제 버튼)
└── TodoForm.tsx       # Todo 생성 폼 (입력 + 제출)

app/
└── page.tsx           # TodoForm + TodoList 조합 (step 0 파일 수정)
```

### 컴포넌트 시그니처

```typescript
// components/TodoItem.tsx
interface TodoItemProps {
  todo: Todo;
  onStatusChange: (id: string, status: TodoStatus) => void;
  onDelete: (id: string) => void;
}

// components/TodoList.tsx
interface TodoListProps {
  todos: Todo[];
  onStatusChange: (id: string, status: TodoStatus) => void;
  onDelete: (id: string) => void;
}

// components/TodoForm.tsx
interface TodoFormProps {
  onSubmit: (title: string) => void;
}
```

### 규칙

- `TodoItem`의 체크박스에 `aria-checked`, `aria-label` 속성을 반드시 포함한다. 이유: 접근성 테스트 통과 조건.
- 상태 관리는 `app/page.tsx`에서 `useState`로 처리한다. 컴포넌트 내부에 API 호출 로직을 넣지 마라.
- 빈 title 제출은 폼 레벨에서 막는다 (submit 버튼 disabled 또는 에러 메시지 표시).

## Acceptance Criteria

```bash
npm run build   # 타입 에러 없음
npm test        # 컴포넌트 테스트 통과
```

테스트는 아래 시나리오를 커버해야 한다:
- `TodoItem` — 체크박스에 `aria-checked` 속성 존재
- `TodoItem` — 삭제 버튼 클릭 시 `onDelete` 호출
- `TodoList` — 빈 배열이면 "할 일이 없습니다" 메시지 표시
- `TodoForm` — 빈 입력으로 제출 불가
- `TodoForm` — 유효한 입력 제출 시 `onSubmit` 호출 후 입력 초기화

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - 컴포넌트가 `components/` 폴더에 분리되어 있는가?
   - API 호출이 `app/page.tsx`에서만 이루어지는가? (컴포넌트 내부 API 호출 없음)
   - 접근성 속성(`aria-*`)이 체크박스에 포함되어 있는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 step 3을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "생성된 컴포넌트 목록과 테스트 커버리지 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- 컴포넌트 내부에서 직접 `fetch('/api/todos')`를 호출하지 마라. 이유: ARCHITECTURE.md CRITICAL 규칙 위반 — 클라이언트 컴포넌트의 직접 외부 API 호출 금지.
- `aria-checked` 없이 체크박스를 구현하지 마라. 이유: 접근성 테스트 3개가 이 속성에 의존한다.
- `pages/` 디렉토리를 생성하지 마라. 이유: App Router와 충돌 발생.
- 기존 테스트를 깨뜨리지 마라.
