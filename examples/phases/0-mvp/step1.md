# Step 1: core-types

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/CLAUDE.md`
- `package.json` (설치된 의존성 확인)
- `app/layout.tsx`, `app/page.tsx` (step 0 산출물)

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

`types/todo.ts`에 Todo 도메인 타입을 정의하라.

### 인터페이스 시그니처

```typescript
// types/todo.ts

export type TodoStatus = 'pending' | 'in_progress' | 'done';

export interface Todo {
  id: string;          // UUID
  title: string;
  status: TodoStatus;
  createdAt: string;   // ISO 8601
  updatedAt: string;   // ISO 8601
}

export interface CreateTodoInput {
  title: string;
}

export interface UpdateTodoInput {
  title?: string;
  status?: TodoStatus;
}
```

Zod 스키마도 함께 정의하라 (API 레이어에서 입력 검증에 사용):

```typescript
// types/todo.schema.ts
import { z } from 'zod';

export const createTodoSchema = z.object({ ... });
export const updateTodoSchema = z.object({ ... });
```

### 규칙

- `id`는 서버에서 생성. `CreateTodoInput`에 포함하지 말 것.
- `createdAt`, `updatedAt`은 클라이언트에서 직접 설정 금지. 서버 레이어에서만 주입.

## Acceptance Criteria

```bash
npm run build   # 타입 에러 없음
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - 타입이 `types/` 폴더에 분리되어 있는가?
   - `strict: true` 환경에서 컴파일 에러가 없는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 step 1을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "types/todo.ts 및 types/todo.schema.ts 생성. Todo, TodoStatus, CreateTodoInput, UpdateTodoInput 타입 정의 완료."`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `any` 타입을 사용하지 마라. 이유: strict 모드에서 타입 안전성을 보장해야 한다.
- `id`를 `CreateTodoInput`에 포함하지 마라. 이유: 클라이언트가 ID를 지정하면 충돌 및 보안 문제 발생.
- 기존 테스트를 깨뜨리지 마라.
