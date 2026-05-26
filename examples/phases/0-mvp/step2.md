# Step 2: api-layer

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/CLAUDE.md`
- `package.json` (설치된 의존성 확인)
- `types/todo.ts`, `types/todo.schema.ts` (step 1 산출물)

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

Todo CRUD API 라우트를 구현하라.

### 생성할 파일

```
app/api/todos/
├── route.ts           # GET (목록 조회), POST (생성)
└── [id]/
    └── route.ts       # PATCH (수정), DELETE (삭제)
```

### 엔드포인트 시그니처

```typescript
// app/api/todos/route.ts
export async function GET(request: Request): Promise<Response>
export async function POST(request: Request): Promise<Response>

// app/api/todos/[id]/route.ts
export async function PATCH(
  request: Request,
  { params }: { params: { id: string } }
): Promise<Response>
export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
): Promise<Response>
```

### 응답 규격

| 상황 | 상태 코드 |
|------|----------|
| 성공 (목록/단건) | 200 |
| 생성 성공 | 201 |
| 요청 데이터 오류 | 400 |
| 리소스 없음 | 404 |
| 서버 오류 | 500 |

### 규칙

- 입력 검증은 `types/todo.schema.ts`의 Zod 스키마를 사용한다. 직접 검증 로직을 작성하지 마라.
- `id`는 `crypto.randomUUID()`로 서버에서 생성한다. 클라이언트 입력값을 사용하지 마라.
- `createdAt`, `updatedAt`은 라우트 핸들러에서만 설정한다.
- 저장소는 인메모리 배열(`let todos: Todo[] = []`)로 구현한다. DB 연동은 이 step의 범위가 아니다.

## Acceptance Criteria

```bash
npm run build   # 타입 에러 없음
npm test        # API 라우트 테스트 통과
```

테스트는 아래 시나리오를 커버해야 한다:
- `GET /api/todos` — 빈 배열 반환
- `POST /api/todos` — 유효한 입력으로 Todo 생성
- `POST /api/todos` — 빈 title로 요청 시 400 반환
- `PATCH /api/todos/:id` — status 변경
- `PATCH /api/todos/:id` — 존재하지 않는 id로 요청 시 404 반환
- `DELETE /api/todos/:id` — 삭제 후 목록에서 제거 확인

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - API 라우트가 `app/api/` 경로에만 있는가?
   - Zod 스키마를 통한 입력 검증이 이루어지는가?
   - `id`, `createdAt`, `updatedAt`이 서버에서만 생성되는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 step 2를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "생성된 파일 목록과 테스트 커버리지 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- 클라이언트에서 전달된 `id`를 그대로 사용하지 마라. 이유: 중복 및 보안 취약점 발생.
- `any` 타입을 사용하지 마라. 이유: strict 모드에서 타입 안전성 보장 실패.
- 인메모리 저장소 외 외부 DB, ORM을 도입하지 마라. 이유: 이 step의 범위를 초과한다.
- 기존 테스트를 깨뜨리지 마라.
