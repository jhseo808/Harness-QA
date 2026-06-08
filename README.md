# Harness-QA

Claude Code CLI를 이용해 소프트웨어 개발의 **각 단계(Phase)를 자동 실행**하는 하네스 프레임워크입니다. QA 전문가 에이전트 시스템을 내장하여, 구현 단계부터 테스트 보고서 생성까지 AI가 자율적으로 수행합니다.

---

## 왜 만들었는가

AI 서비스가 빠르게 확산되는 동안, QA 방법론은 그 속도를 따라가지 못하고 있습니다.

전통적인 QA는 결정론적(deterministic) 동작을 전제합니다. 같은 입력에 같은 출력이 나와야 하고, 테스트는 통과 또는 실패로 끝납니다. 그러나 LLM 기반 서비스는 다릅니다. 동일한 질문에도 응답이 매번 달라지고, "틀렸다"가 아니라 "환각이 있다", "출처와 맞지 않는다", "안전하지 않다"는 새로운 실패 유형이 등장합니다. RAG 파이프라인이 추가되면 검색 품질이 응답 품질을 좌우하고, 에이전틱 구조에서는 툴 호출 하나의 오류가 연쇄 실패로 이어집니다.

문제는 **무엇을 테스트해야 하는지조차 팀마다 제각각**이라는 점입니다. 프롬프트를 바꿨을 때 어떤 검증이 필요한지, 모델을 교체했을 때 릴리스를 막을 기준이 무엇인지, RAG 문서가 업데이트됐을 때 어디까지 재검증해야 하는지 — 이 질문들에 체계적으로 답하는 구조가 없는 경우가 대부분입니다.

이 프레임워크는 그 공백을 채우기 위해 설계했습니다. 핵심 아이디어는 두 가지입니다.

**첫째, 서비스 변경 유형에 따라 검증 범위를 자동으로 결정한다.** 순수 생성 AI인지, RAG인지, 에이전틱인지, 모델이 바뀌었는지에 따라 활성화할 테스트 에이전트가 달라집니다. "모든 테스트를 매번 다 돌린다"는 방식은 비용과 시간 면에서 지속 불가능합니다. 4계층 활성화 구조(`activation_matrix`)는 필요한 에이전트만 선택적으로 실행하도록 합니다.

**둘째, 안전성은 타협하지 않는다.** 안전성 기준은 다른 지표의 개선으로 상쇄되지 않습니다. 모델 변경 시 안전 게이트를 통과하지 못하면 사이클 자체가 중단됩니다. 이는 설계 원칙이 아니라 프로세스 레벨에서 강제됩니다.

AI를 활용해 구조를 설계하고, 실무 팀이 바로 가져다 쓸 수 있도록 명세 수준까지 완성하는 것이 이 프로젝트의 목표였습니다.

---

## 개념 이해

### 문제

AI 코딩 도구는 단일 요청에는 강하지만, 수십 개의 순서가 있는 작업을 스스로 이어가는 데는 약합니다.

### 해결

이 프레임워크는 **Step → 실행 → 검증 → 커밋** 사이클을 자동화합니다. 각 Step은 마크다운 파일로 작성된 명세이고, 하네스가 Claude에게 이를 순차적으로 전달하여 코드를 생성하고, AC(수용 기준)를 직접 검증하고, 결과를 `step{N}-result.json`에 기록합니다. 하네스가 이를 읽어 `index.json`을 갱신하며, 실패 시 최대 3회 자가 교정합니다.

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
│   ├── execute.py              # 하네스 핵심 실행기
│   └── test_execute.py         # execute.py 단위 테스트
│
├── agents/qa/                  # QA 에이전트 페르소나 정의 (마크다운)
│   ├── _base.md                # 모든 QA 에이전트 공통 헌장 (팀 계약, 산출물 경로)
│   ├── qa-lead.md              # QA 전략·활성화 agent 결정·품질 게이트 확정
│   ├── requirements-analyst.md
│   ├── test-case-designer.md
│   ├── playwright.md           # 웹 UI E2E 자동화 (Playwright)
│   ├── appium.md               # iOS/Android 모바일 앱 자동화
│   ├── api-tester.md           # REST/GraphQL API 계약 검증
│   ├── ai-service-tester.md    # AI 서비스 연결·응답 경량 검증 (딥QA는 ai-qa 팀)
│   ├── performance-tester.md   # 부하 테스트·SLA 검증
│   ├── security-tester.md      # OWASP Top 10 기반 취약점 탐지
│   └── reporter.md             # 릴리스 의사결정 보고서 합성
│
├── agents/ai-qa/               # AI QA 서브팀 (생성AI·RAG·에이전틱·모델 변경 전담)
│   ├── _base.md                # AI QA 팀 헌장 (AI 3타입 정의, AI 특화 결함 분류, 산출물 경로)
│   ├── ai-qa-lead.md           # 4계층 에이전트 선택, activation_matrix 출력, A/B 설계
│   ├── ai-evaluator.md         # 루브릭·LLM-as-Judge·골든셋·회귀 평가 (항상 실행)
│   ├── ai-safety-tester.md     # 안전성·보안·권한 (항상 실행)
│   ├── ai-perf-observability-tester.md  # 지연·비용·재현성·버전 추적 (항상 실행)
│   ├── gen-quality-tester.md   # 순수 생성 AI 품질·환각·일관성
│   ├── gen-context-tester.md   # 프롬프트 엔지니어링·컨텍스트 관리
│   ├── rag-pipeline-tester.md  # 청킹·임베딩·Vector DB·인덱싱
│   ├── rag-retrieval-tester.md # 검색 품질·출처 일치·권한 필터링
│   ├── agent-planning-tester.md         # 의도 파악·계획 품질·Goal Drift
│   ├── agent-execution-tester.md        # Tool Calling·MCP·연쇄 정합성
│   ├── agent-action-safety-tester.md    # 비가역 작업·안전장치·범위 이탈
│   ├── agent-memory-state-tester.md     # Working/Long-term memory·상태 추적
│   ├── agent-reflection-recovery-tester.md  # 자기 오류 감지·복구
│   ├── agent-multi-agent-tester.md      # 오케스트레이터-워커·태스크 분해·격리
│   ├── model-safety-gate.md             # 안전성 하드 게이트 (통과 못하면 사이클 중단)
│   ├── model-capability-evaluator.md    # 벤치마크 회귀·골든셋 비교·A/B
│   ├── model-alignment-tester.md        # 정직성·Sycophancy·Constitutional AI
│   ├── model-compatibility-tester.md    # API 형식·프롬프트 하위 호환·Tool Calling
│   ├── model-human-evaluator.md         # 전문가 평가·선호도 비교·레드팀
│   ├── model-rollout-monitor.md         # 단계적 배포·모니터링·롤백 기준
│   └── ai-generated-output-tester.md    # AI 생성 코드·테스트케이스·문서 품질 검증
│
├── datasets/                   # AI QA 테스트 데이터 인프라
│   ├── manifest.yaml           # Suite 정의 (smoke·release·rag_release·agentic_release·model_change·nightly)
│   ├── schemas/                # JSON Schema (test-case, result, rubric, activation-matrix)
│   ├── rubrics/                # 평가 루브릭 (default.yaml, safety.yaml, alignment.yaml)
│   ├── test-cases/             # 카테고리별 테스트 케이스
│   │   ├── capability/
│   │   ├── safety/
│   │   ├── injection/          # direct, indirect, jailbreak, agent-specific
│   │   └── hallucination/      # factual, reference, rag-grounding, self-knowledge
│   ├── golden/                 # 골든 데이터셋 (검증된 정답)
│   ├── baselines/              # 모델별 승인된 기준 지표
│   ├── results/                # 실행 결과 (append-only, version_snapshot 포함)
│   └── docs/                   # 데이터셋 관리 문서
│
├── examples/phases/            # 실행 가능한 예제
│   ├── index.json              # 전체 phase 목록
│   ├── 0-mvp/                  # MVP 구현 phase (일반 개발 예제)
│   │   ├── index.json
│   │   └── step0.md ~ step4.md
│   ├── 1-qa-cycle/             # QA 사이클 phase (일반 QA 에이전트 예제)
│   │   ├── index.json
│   │   └── step0.md ~ step5.md # qa-lead → requirements → test-case → api → playwright → reporter
│   └── 2-ai-qa-cycle/          # AI QA 사이클 phase (RAG 챗봇 대상 예제)
│       ├── index.json
│       └── step0.md ~ step6.md # ai-qa-lead → ai-evaluator → rag-pipeline → rag-retrieval → ai-perf → ai-safety → reporter
│
├── docs/                       # 프로젝트 문서 템플릿 (실제 프로젝트에서 채울 것)
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── ADR.md
│
├── .claude/
│   ├── CLAUDE.md               # 프로젝트별 기술 스택·아키텍처 규칙 템플릿
│   └── commands/
│       ├── harness.md          # /harness 슬래시 커맨드 (step 설계 워크플로우)
│       └── review.md           # /review 슬래시 커맨드
│
├── CLAUDE.md                   # Claude 행동 지침 (전역)
└── requirements.txt            # Python 의존성 (pytest)
```

---

## 빠른 시작

### 사전 조건

- Python 3.8+
- Claude Code CLI 설치 (`claude` 명령어 사용 가능)
- Git 저장소 (자동 브랜치/커밋에 필요)

```bash
pip install -r requirements.txt
```

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
{ "step": 3, "name": "qa-web",    "status": "pending", "agent": "qa/playwright" }
{ "step": 0, "name": "ai-qa-lead","status": "pending", "agent": "ai-qa/ai-qa-lead" }
```

하네스는 `/` 앞의 도메인에 따라 `_base.md`를 자동 로드하고 에이전트 파일을 그 위에 합칩니다:

- `"agent": "qa/playwright"` → `agents/qa/_base.md` + `agents/qa/playwright.md`
- `"agent": "ai-qa/rag-pipeline-tester"` → `agents/ai-qa/_base.md` + `agents/ai-qa/rag-pipeline-tester.md`

### 제공 QA 에이전트

**일반 QA 팀 (`qa/`)**

| 에이전트 | 역할 |
|---------|------|
| `qa/qa-lead` | QA 전략 수립, 활성화 agent 결정, 품질 게이트 확정 |
| `qa/requirements-analyst` | 요구사항 완전성·일관성·검증가능성 분석 |
| `qa/test-case-designer` | 동등분할·경계값·상태전이 기법으로 TC 설계 |
| `qa/playwright` | 웹 UI E2E 자동화 (Page Object Model, playwright-cli 기반) |
| `qa/appium` | iOS/Android 모바일 앱 자동화 |
| `qa/api-tester` | REST/GraphQL API 계약 검증, 보안 경계 테스트 |
| `qa/ai-service-tester` | AI 서비스 연결·응답 경량 검증 (딥 QA는 `ai-qa/` 팀으로 라우팅) |
| `qa/performance-tester` | 부하 테스트, SLA 충족 여부 검증 |
| `qa/security-tester` | OWASP Top 10 기반 취약점 탐지 |
| `qa/reporter` | 전체 테스트 결과를 릴리스 의사결정 보고서로 합성 |

**AI QA 서브팀 (`ai-qa/`) — AI 서비스 전담**

4계층 선택 구조로 필요한 에이전트만 활성화됩니다. `ai-qa-lead`가 `activation_matrix.json`을 출력하면 orchestrator가 이를 읽어 병렬 실행합니다.

| 계층 | 에이전트 | 조건 |
|------|---------|------|
| Layer 0 (항상) | `ai-qa/ai-evaluator`, `ai-qa/ai-safety-tester`, `ai-qa/ai-perf-observability-tester` | 모든 AI 서비스 |
| Layer 1 (서비스 타입) | `ai-qa/gen-quality-tester`, `ai-qa/gen-context-tester` | 순수 생성 AI |
| Layer 1 (서비스 타입) | `ai-qa/rag-pipeline-tester`, `ai-qa/rag-retrieval-tester` | RAG 서비스 |
| Layer 1 (서비스 타입) | `ai-qa/agent-planning-tester`, `ai-qa/agent-execution-tester`, `ai-qa/agent-action-safety-tester` | 에이전틱 AI |
| Layer 2 (복잡도) | `ai-qa/agent-memory-state-tester`, `ai-qa/agent-reflection-recovery-tester`, `ai-qa/agent-multi-agent-tester` | 멀티에이전트 구조 |
| Layer 3 (모델 변경) | `ai-qa/model-safety-gate` → `ai-qa/model-capability-evaluator`, `ai-qa/model-alignment-tester`, `ai-qa/model-compatibility-tester`, `ai-qa/model-human-evaluator`, `ai-qa/model-rollout-monitor` | 모델·알고리즘 변경 시 |
| Layer 4 (AI 산출물) | `ai-qa/ai-generated-output-tester` | AI 생성 코드·문서 릴리스 시 |

### 에이전트 간 데이터 흐름

```
[qa-lead]  ← qa-output/qa-strategy.md 산출 (이후 agent들이 참조)
        │
        ├─→ [일반 QA 경로]
        │       requirements-analyst → test-case-designer
        │           ↓ [TC 목록, 커버리지 매트릭스]
        │           ├─→ playwright / appium / api-tester
        │           ├─→ performance-tester / security-tester
        │           │       ↓ [*-result.md + *-summary.json]
        │           └──────→ reporter
        │
        └─→ [AI QA 경로] ai-service-tester가 딥 QA 필요 판단 시
                ai-qa-lead
                    ↓ qa-output/ai-qa-strategy.md + qa-output/activation-matrix.json
                    │
                    ├─[setup]  ai-evaluator (루브릭·데이터셋 확정)
                    ├─[service, 병렬] 서비스 타입 에이전트 + ai-perf-observability-tester
                    ├─[final]  ai-safety-tester
                    └──────────→ reporter
                                    ↓ qa-output/release-report.md
```

실행 에이전트는 Markdown 결과 리포트(`*-result.md`)와 구조화 요약(`*-summary.json`)을 `qa-output/`에 작성합니다. reporter는 JSON을 우선 읽고, 없으면 Markdown으로 fallback합니다.

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
chore(0-mvp): step 2 output        ← index.json, step2-result.json
```

`qa-output/`은 `.gitignore`에 등록되어 있으므로 커밋에 포함되지 않습니다. 릴리스 보고서 등 외부 공유가 필요한 산출물은 별도 채널(이슈 첨부, 내부 스토리지 등)을 통해 관리하세요.

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

## 결과 파일 작성
작업 완료 후 step{N}-result.json 작성 방법 명시 (index.json은 하네스가 자동 갱신)

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

**일반 품질 게이트**
- P0 결함 0건
- P1 결함 수정 완료 또는 릴리스 책임자 승인
- 핵심 사용자 플로우 커버리지 100%
- 자동화 테스트 통과율 95% 이상
- 보안 Critical 취약점 0건
- 성능 SLA 충족 (P95 응답시간 < 1000ms)
- 테스트 결과 보고서 작성 완료

**AI QA 추가 게이트** (AI 서비스 변경 시)
- AI 안전성 100% — 단 한 건의 유해 응답도 허용 안 됨 (타 지표로 상쇄 불가)
- AI 정확도 ≥ 90%
- RAG 출처 일치율 ≥ 95% (RAG 서비스인 경우)
- 모델 안전 게이트 통과 (모델·알고리즘 변경 시, 미통과 시 사이클 즉시 중단)
- 에이전틱 액션 안전성 통과 (에이전틱 AI인 경우)
