# Step 0: project-setup

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/CLAUDE.md`

## 작업

Next.js 15 + TypeScript + Tailwind CSS 기반 프로젝트를 초기화하라.

### 생성할 파일

```
my-todo-app/
├── package.json          # next, react, typescript, tailwindcss 의존성 포함
├── tsconfig.json         # strict: true 필수
├── tailwind.config.ts
├── next.config.ts
├── app/
│   ├── layout.tsx        # RootLayout
│   └── page.tsx          # 빈 홈 페이지 (Hello World 수준)
└── .env.example          # 필요한 환경변수 목록 (값 없이 키만)
```

### 규칙

- `tsconfig.json`의 `strict: true`를 반드시 켤 것. 이후 step에서 타입 에러 방지.
- `app/` 디렉토리 구조를 Next.js App Router 방식으로 구성. Pages Router 사용 금지.
- `.env.example`에는 값 없이 키만 기록. 실제 값은 절대 커밋하지 말 것.

## Acceptance Criteria

```bash
npm run build   # 컴파일 에러 없음
npm run lint    # ESLint 에러 없음
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md의 디렉토리 구조(`app/`, `components/`, `types/`, `lib/`, `services/`)가 준비되었는가?
   - ADR의 기술 스택(Next.js 15, TypeScript strict, Tailwind)을 따르는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 step 0을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "생성된 파일 목록과 핵심 설정 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `pages/` 디렉토리를 생성하지 마라. 이유: App Router와 Pages Router 혼용 시 Next.js 15에서 라우팅 충돌 발생.
- 데모용 더미 컴포넌트를 만들지 마라. 이유: 이후 step에서 타입 불일치 유발.
- 기존 테스트를 깨뜨리지 마라.
