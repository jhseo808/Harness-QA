# 하네스 구조 평가: assess-20260614-001

## 요약

| 항목 | 내용 |
|---|---|
| 평가일 | 2026-06-14 |
| 루브릭 | harness-structure-rubric.v1 |
| 하네스 커밋 | bb0d794 |
| Working tree | dirty |
| 평가자 | Codex / GPT-5 |
| 비교 대상 | none |
| 점수 | 89 / 100 |
| 등급 | 구조는 있으나 무거움 |

## 핵심 판단

현재 하네스는 실행기, step 계약, agent 체계, AI-QA dataset 구조, 온보딩 문서까지 갖춘 강한 템플릿이다. 다만 여러 QA팀이 가볍게 가져가서 계속 바꾸며 쓰기에는 일반 QA와 AI-QA의 경계가 일부 섞여 있고, activation matrix 실행 흐름이 수동 절차에 의존하며, `/harness` 설명과 실제 실행기의 `qa-output` 커밋 정책이 어긋난다.

따라서 지금 상태는 바로 활용 가능한 구조이지만, 95점 이상의 목표 성숙도를 위해서는 Core 경량화와 확장 경계 정리가 필요하다.

## 점수 상세

| 영역 | 점수 | 근거 |
|---|---:|---|
| Core 실행 방식 | 18 / 20 | `scripts/execute.py`가 pending step 선택, 상태 전이, result 검증, 재시도, 복구, agent 주입, commit 분리를 제공한다. 다만 Claude CLI 호출 방식이 직접 박혀 있어 모델/도구 교체 경계가 약하다. |
| Step/상태/Result 계약 | 14 / 15 | `stepN-result.json` 계약과 index 반영 책임이 명확하다. 단, `/harness`는 `qa-output`을 chore 커밋에 포함한다고 설명하지만 실행기는 제외한다. |
| QA Agent 구조 | 17 / 20 | 일반 QA와 AI-QA agent 역할이 폭넓게 분리되어 있고 `_base.md` 계약도 있다. 다만 `qa/_base.md`에 AI-QA 산출물까지 포함되어 경계가 흐리고, agent 수와 설명량이 많아 경량성이 떨어진다. |
| Core와 선택 확장 경계 | 12 / 15 | Core 실행기는 dataset에 직접 의존하지 않지만, AI-QA/dataset/activation matrix가 템플릿 안에서 큰 비중을 차지한다. matrix 실행은 수동 변환에 의존한다. |
| 온보딩/유지보수 구조 | 14 / 15 | README, GETTING_STARTED, datasets docs, activation matrix guide가 도입과 확장 경로를 설명한다. 다만 변경 시 반드시 함께 갱신해야 할 파일 목록은 아직 분산되어 있다. |
| 예시/템플릿 구조 | 9 / 10 | 0-mvp, 일반 QA, AI-QA 예시가 모두 있다. 다만 최소 Core 예시는 일부 completed 상태와 프로젝트 예시가 섞여 순수 복사용 템플릿으로는 덜 가볍다. |
| 평가 이력 구조 | 5 / 5 | legacy 분리, 고정 루브릭, run 기반 결과, history/latest 구조가 마련되어 있다. |

## 주요 강점

- `scripts/execute.py`의 실행 루프가 단순하고 추적 가능하다.
- result 파일만 agent가 쓰고 index는 실행기가 갱신하는 단방향 계약이 좋다.
- 일반 QA와 AI-QA agent 범위가 실무적으로 넓고 구체적이다.
- AI-QA dataset 구조가 manifest, schema, suite, owner_agent, result storage로 연결되어 있다.
- README와 GETTING_STARTED가 새 QA팀의 초기 도입 경로를 제공한다.
- assessments 체계가 legacy와 새 run 기반 구조를 분리한다.

## 구조적 리스크

- `qa/_base.md`의 산출물 경로 표에 AI-QA agent 전체가 들어 있어 일반 QA Core와 AI-QA 확장 경계가 흐리다.
- `.claude/commands/harness.md`의 2단계 커밋 설명과 `scripts/execute.py`의 실제 `qa-output` 제외 정책이 다르다.
- activation matrix는 좋은 선택 구조지만, 실행기는 이를 읽지 않으므로 수동 변환 실수 가능성이 있다.
- Core 실행기가 Claude CLI 호출에 직접 묶여 있어 모델/도구 변경 내성이 완전하지 않다.
- agent와 dataset 구조가 강력한 만큼, 최소 도입 관점에서는 무겁게 느껴질 수 있다.

## Core/확장 경계 검토

Core는 `index.json`과 `step*.md`, `stepN-result.json`, agent 주입, 상태 전이만으로 작동한다. 이 점은 좋다. 그러나 템플릿 패키지 전체에서는 AI-QA와 dataset이 매우 큰 비중을 차지하고, 일반 QA base에도 AI-QA 산출물 계약이 들어가 있어 “작은 Core + 선택 확장”의 체감 경계가 약해진다.

AI-QA는 선택 확장으로 유지하는 것이 맞다. 이를 위해 일반 QA base를 더 가볍게 만들고, AI-QA 산출물/데이터셋/suite 계약은 AI-QA base와 datasets 문서로 모으는 것이 좋다.

## Agent 구조 검토

일반 QA agent는 요구사항, 테스트케이스, API, UI, 모바일, 성능, 보안, 보고 역할로 충분히 분리되어 있다. AI-QA agent는 생성AI, RAG, agentic, 모델 변경, AI 생성 산출물 검증까지 폭넓게 커버한다.

다만 agent 프롬프트는 실무 지식이 풍부한 대신 길고 무겁다. `_base.md`와 개별 agent 사이에 중복 설명이 늘어나면 모델 변경이나 agent 추가 시 유지보수 비용이 커질 수 있다. 특히 `qa/_base.md`의 AI-QA 산출물 혼입은 우선 정리할 필요가 있다.

## 온보딩/유지보수 구조 검토

README와 GETTING_STARTED는 새 팀이 어떤 파일을 채워야 하는지 안내한다. datasets 문서와 activation matrix guide도 확장 흐름을 설명한다. 평가 체계도 assessments에 분리되어 있다.

부족한 점은 “하네스 변경 체크리스트”다. 예를 들어 agent를 추가하면 README, `/harness`, `_base.md`, examples, datasets manifest, assessments rubric 중 무엇을 함께 갱신해야 하는지 한눈에 보이는 표가 아직 없다. 하네스가 자주 바뀔 전제라면 이 체크리스트가 유지보수 안정성을 크게 높인다.

## 모델/하네스 변경 내성 검토

모델 변경을 위한 `model-safety-gate`, `model-capability-evaluator`, `model-compatibility-tester`, `model-rollout-monitor` agent가 있어 AI-QA 관점의 변경 내성은 강하다. 결과 저장 구조도 `model_id`, `dataset_version`, `run_id`, `version_snapshot` 개념을 갖는다.

반면 하네스 실행 Core의 모델/도구 호출부는 `claude -p` 호출에 직접 묶여 있다. 하네스 자체가 여러 모델 또는 실행 도구로 확장될 가능성이 있다면 adapter 경계를 문서와 코드에 더 명확히 두는 것이 좋다.

## 이전 평가 대비 변경 사항

첫 run이므로 비교 대상은 없다. `assessments/legacy/`의 v1.x 평가는 역사적 맥락으로만 참고했다.

현재 평가는 dirty working tree 기준이다. 따라서 bb0d794 커밋과 미커밋 변경이 함께 반영되어 있다.

## 평가자/모델 기록

| 항목 | 내용 |
|---|---|
| 평가 도구 | Codex |
| 모델 계열 | GPT-5 |
| 사용 이유 | Claude Code 중심으로 작성/실행되는 하네스를 다른 모델 계열로 평가해 자기평가 편향을 줄이기 위함 |

## 개선 우선순위

1. P0: `qa/_base.md`와 `ai-qa/_base.md`의 산출물/역할 계약 경계를 분리한다.
2. P0: `/harness`의 `qa-output` 커밋 설명을 실제 실행기 정책과 일치시킨다.
3. P1: activation matrix에서 후속 step을 만드는 표준 계약을 더 강하게 고정한다.
4. P1: Claude CLI 호출부를 adapter 경계로 분리한다.
5. P2: 최소 Core만 보여주는 가벼운 예시 phase를 추가한다.

## 95점 목표 개선안

| 우선순위 | 개선 항목 | 관련 영역 | 예상 점수 개선 | 난이도 | 이유 | 제안 수정 |
|---|---|---|---:|---|---|---|
| P0 | 일반 QA base와 AI-QA base의 산출물/역할 계약 분리 | QA Agent 구조, Core와 선택 확장 경계 | 3 | medium | 새 QA팀이 일반 QA만 도입할 때 AI-QA 전체 산출물 표를 함께 이해해야 한다. | `agents/qa/_base.md`에는 일반 QA 산출물과 공통 result 계약만 남기고 AI-QA 산출물은 `agents/ai-qa/_base.md`와 README AI-QA 섹션으로 한정한다. |
| P0 | `qa-output` 커밋 정책 불일치 수정 | Step/상태/Result 계약, 온보딩/유지보수 구조 | 2 | low | slash command와 실행기 설명이 다르면 산출물 보관 정책을 오해한다. | `.claude/commands/harness.md`의 2단계 커밋 설명을 “result/index는 커밋, qa-output은 기본 제외”로 수정한다. |
| P1 | activation matrix → step 변환 계약 표준화 | Core와 선택 확장 경계, 예시/템플릿 구조 | 2 | medium | 현재는 수동 가이드에 의존해 변환 실수가 생길 수 있다. | 변환 결과의 표준 index/step 예시와 required/skipped/parallel_group 처리 규칙을 템플릿으로 고정한다. |
| P1 | 모델/도구 호출 adapter 경계 도입 | Core 실행 방식, 모델/하네스 변경 내성 | 2 | medium | Claude CLI 직접 호출은 모델/도구 변경 시 수정 범위를 키운다. | `scripts/execute.py`에서 호출부를 별도 메서드/adapter 설정으로 분리하고 README에 교체 지점을 명시한다. |
| P2 | 최소 Core 예시 경량화 | 예시/템플릿 구조, 온보딩/유지보수 구조 | 1 | low | 0-mvp 예시는 유용하지만 순수 복사용 최소 템플릿으로는 덜 가볍다. | `examples/phases/minimal-core` 또는 pending-only 예시를 추가한다. |

## 근거

- `scripts/execute.py`
- `.claude/commands/harness.md`
- `agents/qa/_base.md`
- `agents/ai-qa/_base.md`
- `README.md`
- `GETTING_STARTED.md`
- `docs/ACTIVATION_MATRIX_GUIDE.md`
- `datasets/manifest.yaml`
- `datasets/README.md`
- `examples/phases/index.json`
- `examples/phases/0-mvp/index.json`
- `examples/phases/1-qa-cycle/index.json`
- `examples/phases/2-ai-qa-cycle/index.json`
- `assessments/rubrics/harness-structure-rubric.v1.md`
- `assessments/templates/harness-assessment-prompt.md`
- `assessments/history.md`
