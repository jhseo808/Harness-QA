# Getting Started

Harness-QA를 새 프로젝트에 적용하는 단계별 가이드입니다.
클론부터 첫 phase 실행까지 10분 안에 완료할 수 있습니다.

---

## 사전 조건

- Python 3.8+
- Claude Code CLI 설치 및 로그인 (`claude --version` 으로 확인)
- Git 저장소 (`git init` 또는 기존 저장소)

---

## 1단계: 클론 및 설치

```bash
git clone <this-repo> harness-qa
cd harness-qa
pip install -r requirements.txt
```

---

## 2단계: `.claude/CLAUDE.md` 작성

`.claude/CLAUDE.md`는 하네스가 **모든 Claude 호출에 자동 주입하는 프로젝트 컨텍스트**입니다.
파일 상단의 템플릿 안내 주석을 읽고, `{중괄호}` 항목을 실제 프로젝트에 맞게 채우세요.

채워야 할 항목:

| 섹션 | 예시 |
|------|------|
| 프로젝트명 | `My Chatbot Service` |
| 기술 스택 | `Next.js 15`, `TypeScript strict mode`, `Tailwind CSS` |
| CRITICAL 아키텍처 규칙 | `"API 로직은 app/api/ 에서만"`, `"클라이언트 컴포넌트에서 외부 API 직접 호출 금지"` |
| 개발 명령어 | `npm run dev`, `npm test`, `npm run build` |

**작성 완료 후 파일 상단 주석을 삭제하세요.**

> 이 파일을 채우지 않으면 Claude가 프로젝트 기술 스택을 알 수 없어 엉뚱한 프레임워크로 코드를 생성할 수 있습니다.

---

## 3단계: `docs/` 작성

하네스는 `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`를 가드레일로 자동 주입합니다.
현재 세 파일 모두 빈 템플릿입니다. 프로젝트 내용으로 채우세요.

| 파일 | 필수 내용 | 없으면 |
|------|---------|--------|
| `docs/PRD.md` | 제품 목표, 핵심 기능, MVP 범위 | Claude가 임의로 기능 범위를 결정 |
| `docs/ARCHITECTURE.md` | 디렉토리 구조, 디자인 패턴, 데이터 흐름 | 구조 일관성 없이 파일을 생성 |
| `docs/ADR.md` | 기술 스택 선택 이유, 주요 의사결정 | 이미 결정된 기술을 재논의하거나 교체 |

> 초기에는 간략해도 됩니다. Claude가 이 파일들을 읽고 구현 방향을 결정합니다.

---

## 4단계: Phase 설계

Claude Code에서 `/harness` 명령어를 입력하면 step 설계 워크플로우가 시작됩니다.

```
/harness
```

워크플로우 순서:

| 단계 | Claude의 행동 | 내가 할 일 |
|------|-------------|-----------|
| A (탐색) | `docs/`를 읽고 프로젝트 파악 | — |
| B (논의) | 기술 결정 사항 질문 | 답변 |
| C (설계) | Step 목록 초안 제시 | 피드백, 승인 |
| D (생성) | `phases/` 아래 파일 생성 | — |
| E (실행) | `execute.py` 명령 안내 | 명령 실행 |

**에이전트 지정:** 특정 step에 QA 에이전트가 필요하면 `/harness` 설계 시 명시하세요.

```json
{ "step": 3, "name": "qa-web",    "agent": "qa/playwright" }
{ "step": 0, "name": "ai-qa-lead","agent": "ai-qa/ai-qa-lead" }
```

전체 에이전트 목록은 README.md의 "에이전트 시스템" 섹션을 참고하세요.

---

## 5단계: 실행

```bash
# 기본 실행
python scripts/execute.py 0-mvp

# 완료 후 원격 push까지 자동화
python scripts/execute.py 0-mvp --push
```

실행 중 멈추면:

**`error` 상태 — 3회 재시도 후 실패:**
```json
// phases/0-mvp/index.json 에서 해당 step 수정
{ "step": 2, "status": "pending", "error_message": "" }
```
이후 재실행.

**`blocked` 상태 — 수동 개입 필요 (API 키, 환경 설정 등):**
`blocked_reason`의 조건을 해결한 뒤 `status`를 `"pending"`으로 변경 후 재실행.

---

## 예제로 먼저 확인하기

`examples/phases/` 에 실행 가능한 예제가 있습니다. **처음이라면 `minimal-core`부터 시작하세요.**

| 예제 | 내용 |
|------|------|
| `examples/phases/minimal-core/` | **Core 전용 최소 예제** — agent 없이 index.json·step.md·result.json 계약만 확인하는 3-step. 하네스 실행 흐름을 처음 익힐 때 시작점. |
| `examples/phases/0-mvp/` | 일반 개발 phase (Next.js 앱 초기화 → 타입 → API → UI) |
| `examples/phases/1-qa-cycle/` | 일반 QA 사이클 (요구사항 분석 → TC 설계 → 실행 → 보고서) |
| `examples/phases/2-ai-qa-cycle/` | AI QA 사이클 (RAG 챗봇 릴리스 전체 검증 흐름) |

step 파일 하나를 열어 형식을 확인한 뒤 작성하는 것을 권장합니다.

---

## 다음 단계

- **AI QA 도입:** `examples/phases/2-ai-qa-cycle/`과 `datasets/README.md` 참고
- **데이터셋 구축:** `datasets/README.md` → "처음 사용한다면" 섹션
- **에이전트 커스터마이징:** `agents/qa/` 또는 `agents/ai-qa/` 파일을 직접 수정

---

## 하네스 구조 평가

하네스 자체의 구조가 얼마나 견고한지 주기적으로 평가할 수 있습니다.
평가 대상은 QA 실행 결과가 아니라 실행 방식·step 계약·agent 구조·확장 경계·온보딩 구조입니다.

**현재 점수:** 95 / 100 — 매우 우수한 구조 (`assessments/latest.md`)

### 평가 요청 방법

하네스 구조를 크게 변경한 뒤 아래 프롬프트를 사용합니다.

```text
assessments/templates/harness-assessment-prompt.md 기준으로
현재 하네스 구조를 평가해줘.
루브릭은 assessments/rubrics/harness-structure-rubric.v1.md를 사용하고,
결과는 새 assessments/runs/assess-YYYYMMDD-NNN/에 남겨줘.
```

권장 평가자: **Codex** — 하네스 작성 환경(Claude Code)과 다른 모델 계열로 평가해 자기평가 편향을 줄입니다.

### 평가 결과 위치

```
assessments/
├── latest.md        # 최신 평가 요약 (점수, 등급, 핵심 리스크)
├── history.md       # 전체 이력 (run별 한 줄 요약)
└── runs/            # run 단위 상세 결과
    └── assess-YYYYMMDD-NNN/
        ├── report.md        # 영역별 점수·강점·리스크·개선 우선순위
        ├── assessment.json  # 기계 비교용 점수 요약
        └── snapshot.md      # 평가 당시 하네스 구조 스냅샷
```
