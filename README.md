# Harness-QA

Claude Code CLI를 이용해 소프트웨어 개발의 **각 단계(Phase)를 자동 실행**하는 하네스 프레임워크입니다. QA 전문가 에이전트 시스템을 내장하여, 구현 단계부터 테스트 보고서 생성까지 AI가 자율적으로 수행합니다.

---

## 개념 이해

### 문제

AI 코딩 도구는 단일 요청에는 강하지만, 수십 개의 순서가 있는 작업을 스스로 이어가는 데는 약합니다.

### 해결

이 프레임워크는 **Step → 실행 → 검증 → 커밋** 사이클을 자동화합니다. 각 Step은 마크다운 파일로 작성된 명세이고, 하네스가 Claude에게 이를 순차적으로 전달하여 코드를 생성하고, AC(수용 기준)를 직접 검증하고, 결과를 `index.json`에 기록합니다. 실패 시 최대 3회 자가 교정합니다.

```
phases/0-mvp/
├── index.json     # Phase 상태 추적 (step별 status, summary, timestamp)
├── step0.md       # 프로젝트 초기화 명세
├── step1.md       # 타입 정의 명세
├── step2.md       # API 레이어 명세
└── step3.md       # UI 컴포넌트 명세 (agent: "qa/playwright" 지정 가능)
```

---

## 디렉토리 구조

```
Harness-QA/
├── scripts/
│   ├── execute.py          # 하네스 핵심 실행기
│   └── test_execute.py     # execute.py 단위 테스트
│
├── agents/qa/              # QA 에이전트 페르소나 정의 (마크다운)
│   ├── _base.md            # 모든 QA 에이전트 공통 헌장
│   ├── requirements-analyst.md
│   ├── test-case-designer.md
│   ├── playwright.md       # 웹 UI 자동화 (Playwright)
│   ├── appium.md           # 모바일 앱 자동화
│   ├── api-tester.md       # REST/GraphQL API 테스트
│   ├── ai-service-tester.md
│   ├── performance-tester.md
│   ├── security-tester.md
│   └── reporter.md
│
├── examples/phases/        # 실제 사용 예제 (my-todo-app)
│   ├── index.json          # 전체 phase 목록 및 상태
│   └── 0-mvp/
│       ├── index.json      # Phase 상태 (step별 status/summary)
│       ├── step0.md        # 프로젝트 초기화
│       ├── step1.md        # 타입 정의
│       └── step4.md        # QA 자동화 (qa/playwright 에이전트)
│
├── docs/                   # 프로젝트 문서 템플릿
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── ADR.md
│
├── CLAUDE.md               # Claude 행동 지침 (전역)
└── .claude/CLAUDE.md       # 프로젝트별 지침 템플릿
```

---

## 빠른 시작

### 사전 조건

- Python 3.8+
- Claude Code CLI 설치 (`claude` 명령어 사용 가능)
- Git 저장소 (자동 브랜치/커밋에 필요)

### 1. Phase 구조 작성

```
your-project/
└── phases/
    ├── index.json        # 전체 phase 목록
    └── 0-mvp/
        ├── index.json    # 이 Phase의 step 목록
        ├── step0.md      # 첫 번째 step 명세
        └── step1.md      # 두 번째 step 명세
```

**`phases/0-mvp/index.json` 예시:**

```json
{
  "project": "my-app",
  "phase": "0-mvp",
  "steps": [
    { "step": 0, "name": "project-setup", "status": "pending" },
    { "step": 1, "name": "core-types",    "status": "pending" },
    { "step": 2, "name": "api-layer",     "status": "pending" },
    { "step": 3, "name": "qa-web",        "status": "pending", "agent": "qa/playwright" }
  ]
}
```

**`phases/0-mvp/step0.md` 예시:**

```markdown
# Step 0: project-setup

## 작업
Next.js 15 + TypeScript + Tailwind CSS 기반 프로젝트를 초기화하라.

## Acceptance Criteria
\`\`\`bash
npm run build   # 컴파일 에러 없음
npm run lint    # ESLint 에러 없음
\`\`\`
```

### 2. 실행

```bash
python scripts/execute.py 0-mvp
```

완료 후 원격 저장소에 자동 Push:

```bash
python scripts/execute.py 0-mvp --push
```

---

## 실행 흐름

```
execute.py 시작
    │
    ├─ 1. 블로커 확인 (error/blocked 상태인 step 있으면 중단)
    ├─ 2. Git 브랜치 체크아웃 (feat-{phase-name})
    ├─ 3. 가드레일 로드 (CLAUDE.md + .claude/CLAUDE.md + docs/*.md)
    │
    └─ Step 순환 루프
         │
         ├─ pending인 step 선택
         ├─ 에이전트 로드 (step의 "agent" 필드 → agents/ 디렉토리)
         ├─ 프리앰블 조립 (가드레일 + 이전 step 산출물 + 작업 규칙)
         ├─ Claude 호출: claude -p --dangerously-skip-permissions
         │
         ├─ [completed] → index.json 업데이트 + Git 커밋 → 다음 step
         ├─ [blocked]   → 사유 출력 후 종료 (exit 2)
         └─ [error/미갱신] → 재시도 (최대 3회) → 최종 실패 시 종료 (exit 1)
```

### Step 상태 전이

| 상태 | 의미 | 다음 행동 |
|------|------|----------|
| `pending` | 대기 중 | 하네스가 자동 실행 |
| `completed` | 성공 | `summary` 필드에 산출물 요약 기록됨 |
| `error` | 3회 재시도 후 실패 | `error_message` 확인 후 `pending`으로 되돌려 재실행 |
| `blocked` | 수동 개입 필요 (API 키, 환경설정 등) | `blocked_reason` 확인 후 해결, `pending`으로 재설정 |

---

## 에이전트 시스템

`step<N>.md`에 `agent` 필드를 지정하면 해당 step에 전문가 페르소나가 주입됩니다.

```json
{ "step": 3, "name": "qa-web", "status": "pending", "agent": "qa/playwright" }
```

이 경우 하네스는 다음 두 파일을 로드하여 Claude 프롬프트에 포함합니다:

1. `agents/qa/_base.md` — QA 팀 공통 헌장 (도메인 기반 자동 로드)
2. `agents/qa/playwright.md` — Playwright 전문가 페르소나

### 제공 QA 에이전트

| 에이전트 | 역할 |
|---------|------|
| `qa/requirements-analyst` | 요구사항 완전성·일관성·검증가능성 분석 |
| `qa/test-case-designer` | 동등분할·경계값·상태전이 기법으로 TC 설계 |
| `qa/playwright` | 웹 UI E2E 자동화 (Page Object Model, playwright-cli 기반) |
| `qa/appium` | iOS/Android 모바일 앱 자동화 |
| `qa/api-tester` | REST/GraphQL API 계약 검증, 보안 경계 테스트 |
| `qa/ai-service-tester` | AI 서비스 응답 품질, 안전성, 일관성 검증 |
| `qa/performance-tester` | 부하 테스트, SLA 충족 여부 검증 |
| `qa/security-tester` | OWASP Top 10 기반 취약점 탐지 |
| `qa/reporter` | 전체 테스트 결과를 릴리스 의사결정 보고서로 합성 |

### 에이전트 간 데이터 흐름

```
requirements-analyst
        ↓ [테스트 범위, 리스크 매트릭스, 테스트 전략]
test-case-designer
        ↓ [TC 목록, 커버리지 매트릭스]
        ├─→ playwright / appium / api-tester
        ├─→ ai-service-tester / performance-tester / security-tester
                ↓ [실행 결과, 발견 결함]
            reporter
                ↓ [릴리스 권고 보고서]
```

---

## 가드레일 (Guardrails)

하네스는 Claude 호출 시마다 아래 파일들을 자동으로 컨텍스트에 포함합니다. 프로젝트 규칙이 모든 step에 일관되게 적용됩니다.

| 파일 | 역할 |
|------|------|
| `CLAUDE.md` | 코딩 원칙 (단순함 우선, 외과적 변경, 목표 주도 실행) |
| `.claude/CLAUDE.md` | 프로젝트별 기술 스택, 아키텍처 규칙, 명령어 |
| `docs/PRD.md` | 제품 목표, 핵심 기능, MVP 범위 |
| `docs/ARCHITECTURE.md` | 디렉토리 구조, 디자인 패턴, 데이터 흐름 |
| `docs/ADR.md` | 기술 선택 의사결정 기록 |

---

## 커밋 규칙

하네스는 step 완료 시 두 개의 커밋을 자동 생성합니다.

```
feat(0-mvp): step 2 — api-layer    ← 코드 변경사항
chore(0-mvp): step 2 output        ← index.json, step2-output.json
```

---

## Step 명세 작성 가이드

좋은 Step 명세는 다음 섹션을 포함합니다:

```markdown
# Step N: {이름}

## 읽어야 할 파일
이전 step 산출물, 관련 문서 목록

## 작업
구체적인 구현 내용, 생성할 파일 목록, 지켜야 할 규칙

## Acceptance Criteria
검증 가능한 커맨드 (예: npm test, npm run build)

## 검증 절차
AC 실행 후 index.json 업데이트 방법 명시

## 금지사항
하지 말아야 할 것과 그 이유
```

**핵심 원칙:**
- AC는 반드시 실행 가능한 커맨드로 작성 (주관적 판단 금지)
- 이전 step과의 일관성을 위해 "읽어야 할 파일" 섹션 필수
- 금지사항에는 반드시 이유를 명시

---

## 오류 복구

### `error` 상태로 멈춘 경우

```json
// phases/0-mvp/index.json 에서 해당 step 찾아 수정
{
  "step": 3,
  "name": "ui-components",
  "status": "pending",   // ← "error"에서 "pending"으로 변경
  "error_message": ""    // ← 삭제 또는 비워두기
}
```

이후 `python scripts/execute.py 0-mvp` 재실행.

### `blocked` 상태로 멈춘 경우

`blocked_reason`을 읽고 요구된 조건(API 키 설정, 수동 설정 등)을 해결한 후, 마찬가지로 `status`를 `pending`으로 되돌리고 재실행합니다.

---

## 테스트 실행

```bash
# execute.py 단위 테스트
cd scripts
pytest test_execute.py -v
```

테스트는 `tmp_path` 픽스처 기반으로 실제 파일시스템을 사용하며, Claude 및 Git 호출은 mock 처리됩니다.

---

## 새 프로젝트에 적용하기

1. 이 저장소를 클론하거나 `scripts/execute.py`와 `agents/` 디렉토리를 복사합니다.
2. 프로젝트 루트에 `CLAUDE.md`, `.claude/CLAUDE.md`, `docs/` 를 작성합니다.
   - `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md` 템플릿 참고
3. `phases/<phase-name>/` 디렉토리를 만들고 `index.json`과 `step<N>.md` 파일을 작성합니다.
4. `python scripts/execute.py <phase-name>` 으로 실행합니다.

---

## 품질 게이트 (QA 에이전트 기준)

QA 에이전트가 릴리스 승인을 권고하려면 아래 조건을 모두 만족해야 합니다:

- P0 결함 0건
- P1 결함 수정 완료 또는 릴리스 책임자 승인
- 핵심 사용자 플로우 커버리지 100%
- 자동화 테스트 통과율 95% 이상
- 보안 Critical 취약점 0건
- 성능 SLA 충족 (P95 응답시간 < 1000ms)
- 테스트 결과 보고서 작성 완료
