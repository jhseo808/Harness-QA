# 하네스 구조 평가: assess-20260614-002

## 요약

| 항목 | 내용 |
|---|---|
| 평가일 | 2026-06-14 |
| 루브릭 | harness-structure-rubric.v1 |
| 하네스 커밋 | bb0d794 |
| 평가자 | Codex / GPT-5 |
| 비교 대상 | assess-20260614-001 |
| 점수 | 95 / 100 |
| 등급 | 매우 우수한 구조 |

## 핵심 판단

현재 하네스는 여러 QA팀이 공통 템플릿으로 가져가서 사용할 수 있는 수준까지 구조가 정리되었다.
001 평가에서 지적된 핵심 리스크인 QA/AI-QA base 계약 혼입, `qa-output` 커밋 정책 불일치, 최소 Core 예시 부족, runner 호출 경계 부족이 대부분 개선되었다.

다만 완전히 닫힌 구조는 아니다. `activation_matrix`는 아직 수동 step 변환에 의존하고, 문서 예시에 실제 없는 `ai-qa/reporter` 경로가 남아 있다. 모델/도구 교체 경계도 메서드 수준으로는 생겼지만 설정/문서 수준의 adapter 계약까지는 아직 아니다.

## 점수 상세

| 영역 | 점수 | 근거 |
|---|---:|---|
| Core 실행 방식 | 19 / 20 | `scripts/execute.py`가 pending 선택, 상태 전이, result 검증, stale 필드 제거, 재시도와 복구를 명확히 처리한다. `_build_runner_cmd`로 runner 호출 경계도 생겼다. 다만 Claude CLI 중심 설명과 설정 기반 adapter 부재로 1점 감점했다. |
| Step/상태/Result 계약 | 15 / 15 | `/harness`와 실행기가 `index.json`은 하네스가 갱신하고 agent는 `step{N}-result.json`만 작성한다는 계약을 일치시킨다. `qa-output`은 추적 파일과 분리되어 설명도 실제 동작과 맞는다. |
| QA Agent 구조 | 19 / 20 | 일반 QA와 AI-QA base 산출물 계약이 분리되었고 lead/worker/reporter 구조가 명확하다. 다만 activation guide의 `ai-qa/reporter` 경로 불일치와 agent 수 증가에 따른 유지보수 부담이 남아 1점 감점했다. |
| Core와 선택 확장 경계 | 14 / 15 | Core 실행은 AI-QA/dataset 없이 동작하고, AI-QA는 activation matrix와 dataset suite로 선택 확장된다. 단 matrix는 자동 실행되지 않아 수동 변환 품질에 의존한다. |
| 온보딩/유지보수 구조 | 14 / 15 | README, GETTING_STARTED, docs, datasets, assessments가 도입과 운영 구조를 안내한다. 다만 minimal-core 예시와 runner 교체 경계가 온보딩 문서에서 더 전면화될 필요가 있다. |
| 예시/템플릿 구조 | 9 / 10 | minimal-core, 일반 QA, AI-QA 예시가 모두 존재한다. 하지만 minimal-core가 주요 예시 목록에서 충분히 드러나지 않고 activation guide의 reporter 경로가 어긋나 있다. |
| 평가 이력 구조 | 5 / 5 | rubric, template, runs, latest, history, legacy가 분리되어 반복 평가 구조가 안정적이다. |

## 주요 강점

- `agents/qa/_base.md`가 일반 QA 산출물만 다루고, AI-QA 산출물은 `agents/ai-qa/_base.md`로 분리했다.
- `.claude/commands/harness.md`가 `qa-output/`을 커밋에서 제외한다고 명시해 실행기 동작과 일치한다.
- `scripts/execute.py`가 result 계약을 검증하고 `index.json` 반영 책임을 중앙화한다.
- `docs/ACTIVATION_MATRIX_GUIDE.md`와 schema가 required/skipped 기반 변환 규칙을 제공한다.
- `examples/phases/minimal-core/`가 생겨 가벼운 Core 도입 예시가 마련되었다.
- `assessments/`가 run 단위 평가 이력을 남기므로 하네스 변경 이후 같은 기준으로 재평가할 수 있다.

## 구조적 리스크

- `docs/ACTIVATION_MATRIX_GUIDE.md`의 예시에는 `ai-qa/reporter`가 있지만 실제 파일은 `agents/qa/reporter.md`다.
- runner 호출 경계는 생겼지만 아직 `claude` 명령이 실행기와 README에 강하게 남아 있다.
- activation matrix는 전략 문서와 변환 가이드가 되었지만, 실행기가 자동으로 소비하지는 않는다.
- minimal-core 예시가 추가되었지만 README/GETTING_STARTED의 예시 안내에서 더 눈에 띄게 연결되어야 한다.
- AI-QA agent가 많아질수록 base 계약, schema, docs, examples의 동기화 관리가 중요해진다.

## Core/확장 경계 검토

Core는 `index.json`, `step*.md`, `step{N}-result.json`, `scripts/execute.py`만으로 설명 가능하다.
일반 QA와 AI-QA는 agent 지정과 문서/dataset 구조를 통해 선택 확장으로 얹히는 형태다.

001 대비 가장 큰 개선은 일반 QA base가 AI-QA 산출물 표를 들고 있지 않게 된 점이다.
이로 인해 다른 QA팀이 일반 QA만 도입할 때 이해해야 하는 표면적이 줄었다.

## Agent 구조 검토

일반 QA agent는 요구사항 분석, 테스트 케이스 설계, UI/API/모바일/성능/보안 검증, 보고로 나뉜다.
AI-QA agent는 생성 품질, RAG, agentic, model-change, safety, observability 중심으로 분리되어 있다.

구조 자체는 명확하지만 `ai-qa/reporter` 경로 표기는 실제 agent 구조와 맞지 않는다.
보고 agent를 공통 `qa/reporter`로 쓸지, AI-QA 전용 reporter를 둘지 결정하고 문서를 맞추는 것이 좋다.

## 온보딩/유지보수 구조 검토

README와 GETTING_STARTED는 클론 후 설정, phase 생성, 실행, 커밋, 복구 흐름을 안내한다.
datasets 문서와 activation guide는 AI-QA 확장을 설명하고, assessments는 하네스 자체 평가 이력을 관리한다.

남은 보완점은 경량 도입 경로를 더 앞에 두는 것이다.
`examples/phases/minimal-core/`를 README/GETTING_STARTED 예시 표에 명시하면 새 QA팀이 “먼저 이것만 보면 된다”는 진입점이 더 분명해진다.

## 모델/하네스 변경 내성 검토

하네스는 여전히 Claude Code 중심이지만, runner 명령 조립부가 `_build_runner_cmd`로 분리되어 호출부 교체 지점이 생겼다.
이는 001 대비 분명한 개선이다.

다만 모델 변경을 반복적으로 다룰 템플릿이라면 장기적으로는 provider/model 설정, runner adapter 문서, 또는 최소 환경변수 계약까지 정리하는 편이 좋다.
현재는 95점 수준의 구조 성숙도에는 충분하지만, 98점 이상을 목표로 하면 이 부분이 다음 개선 후보가 된다.

## 이전 평가 대비 변경 사항

| 변경 | 영향 |
|---|---|
| `agents/qa/_base.md`와 `agents/ai-qa/_base.md` 산출물 계약 분리 | QA Agent 구조와 Core/확장 경계 점수 상승 |
| `.claude/commands/harness.md`의 `qa-output` 커밋 정책 정합화 | Step/상태/Result 계약 점수 상승 |
| `scripts/execute.py`의 `_build_runner_cmd` 추가 | Core 실행 방식의 모델 변경 내성 상승 |
| activation matrix required/skipped 변환 규칙 명시 | 선택 확장 경계와 예시 구조 점수 상승 |
| `examples/phases/minimal-core/` 추가 | 최소 Core 예시 항목 개선 |

## 평가자/모델 기록

평가는 Codex / GPT-5로 수행했다.
이 프로젝트의 하네스 작성과 실행 환경은 Claude Code 중심이므로, 구조 평가는 다른 모델 계열로 분리해 자기평가 편향을 줄이는 방식이 적절하다.
단, 완전한 객관성이 자동으로 보장되는 것은 아니므로 모든 판단은 루브릭과 실제 파일 근거에 연결했다.

## 개선 우선순위

| 우선순위 | 개선 항목 | 관련 영역 | 이유 |
|---|---|---|---|
| P0 | activation guide의 `ai-qa/reporter` 경로 정합화 | QA Agent 구조, 예시/템플릿 구조 | 실제 파일 구조와 문서 예시가 다르면 새 팀이 step 변환 시 잘못된 agent를 지정할 수 있다. |
| P1 | README/GETTING_STARTED에 minimal-core 예시 전면 안내 | 온보딩/유지보수, 예시/템플릿 구조 | 하네스가 가볍게 시작된다는 메시지를 새 QA팀이 바로 확인할 수 있다. |
| P1 | runner adapter 교체 지점 문서화 | Core 실행 방식, 모델 변경 내성 | 모델/도구가 바뀔 때 어디를 바꿔야 하는지 명확해진다. |
| P2 | activation matrix 변환 체크리스트 추가 | Core/확장 경계, 유지보수 | matrix, schema, agent 경로, example index가 함께 갱신되도록 관리할 수 있다. |

## 95점 목표 개선안

현재 점수는 95점이므로 95점 목표 보완 항목은 없다.
위 개선 우선순위는 95점 유지와 추가 성숙도 향상을 위한 항목이다.

## 근거

- `scripts/execute.py`
- `.claude/commands/harness.md`
- `agents/qa/_base.md`
- `agents/ai-qa/_base.md`
- `agents/qa/`
- `agents/ai-qa/`
- `README.md`
- `GETTING_STARTED.md`
- `docs/ACTIVATION_MATRIX_GUIDE.md`
- `datasets/manifest.yaml`
- `datasets/schemas/activation-matrix.schema.json`
- `datasets/README.md`
- `examples/phases/minimal-core/index.json`
- `examples/phases/minimal-core/step0.md`
- `examples/phases/minimal-core/step1.md`
- `examples/phases/minimal-core/step2.md`
- `examples/phases/1-qa-cycle/index.json`
- `examples/phases/2-ai-qa-cycle/index.json`
- `assessments/rubrics/harness-structure-rubric.v1.md`
- `assessments/templates/harness-assessment-prompt.md`
- `assessments/runs/assess-20260614-001/assessment.json`
- `assessments/history.md`
