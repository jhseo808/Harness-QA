# 평가 스냅샷: assess-20260614-002

## 기본 정보

| 항목 | 내용 |
|---|---|
| 평가 시각 | 2026-06-14T19:16:36+09:00 |
| Git commit | bb0d794 |
| Working tree | dirty |
| 평가자 | Codex / GPT-5 |
| 루브릭 | harness-structure-rubric.v1 |
| 비교 대상 | assess-20260614-001 |

## 검토한 핵심 구조 파일

- `scripts/execute.py`
- `.claude/commands/harness.md`
- `agents/qa/`
- `agents/ai-qa/`
- `agents/qa/_base.md`
- `agents/ai-qa/_base.md`
- `examples/phases/**/index.json`
- `examples/phases/**/step*.md`
- `datasets/manifest.yaml`
- `datasets/schemas/activation-matrix.schema.json`
- `datasets/README.md`
- `docs/ACTIVATION_MATRIX_GUIDE.md`
- `README.md`
- `GETTING_STARTED.md`
- `assessments/`

## Agent 그룹

| 그룹 | 파일 수 | 관찰 |
|---|---:|---|
| `agents/qa/` | 10 | 일반 QA 흐름의 lead, 요구사항, 테스트 설계, 실행, 보안, 성능, 보고 역할이 분리되어 있다. |
| `agents/ai-qa/` | 22 | 생성AI, RAG, agentic, model-change, safety, observability 관련 전문 agent가 선택 확장으로 구성되어 있다. |

## Example phase 구성

| 예시 | 관찰 |
|---|---|
| `examples/phases/minimal-core/` | `step0.md` ~ `step2.md`와 `index.json`으로 Core 계약만 보여주는 경량 예시가 있다. |
| `examples/phases/0-mvp/` | 일반 개발 phase 흐름을 보여준다. |
| `examples/phases/1-qa-cycle/` | 일반 QA agent 기반 흐름을 보여준다. |
| `examples/phases/2-ai-qa-cycle/` | AI-QA lead와 specialist agent 흐름을 보여준다. |

## AI-QA 확장 연결 구조

- `datasets/manifest.yaml`이 suite, schema, owner_agent, result storage, promotion policy를 연결한다.
- `datasets/schemas/activation-matrix.schema.json`이 activation matrix 형식을 정의한다.
- `docs/ACTIVATION_MATRIX_GUIDE.md`가 `required` agent만 step으로 변환하고 `skipped`는 제외하는 규칙을 설명한다.
- 현재 `execute.py`는 activation matrix를 자동 소비하지 않으며, 후속 step 변환은 수동 절차다.
- 문서 예시의 `ai-qa/reporter` 경로는 실제 agent 파일 구조와 맞지 않는다. 실제 reporter는 `agents/qa/reporter.md`에 있다.

## README/GETTING_STARTED/docs/datasets 안내 구조

- README는 하네스 개념, 디렉터리 구조, 실행 흐름, agent 지정, QA/AI-QA 확장, 커밋 정책, 복구 방법을 설명한다.
- GETTING_STARTED는 클론 후 설정, 첫 phase 실행, 재시도/blocked 복구, 예시 phase 사용법을 안내한다.
- docs는 activation matrix 변환 절차를 보완한다.
- datasets 문서는 AI-QA test case와 suite 운영 구조를 설명한다.
- assessments는 하네스 구조 평가를 run 단위로 반복할 수 있게 한다.

## 변경 시 갱신 경계

| 변경 유형 | 함께 확인할 파일 |
|---|---|
| Core 실행기 변경 | `scripts/execute.py`, `.claude/commands/harness.md`, README의 실행 흐름, minimal-core 예시 |
| Agent 추가/이름 변경 | `agents/**`, `_base.md`, README agent 표, example phase, activation guide |
| AI-QA suite/dataset 변경 | `datasets/manifest.yaml`, `datasets/schemas/`, `datasets/test-cases/`, datasets README |
| activation matrix 변경 | schema, activation guide, 2-ai-qa-cycle 예시, slash command 설명 |
| 모델/도구 호출 변경 | `scripts/execute.py`의 runner 호출부, README prerequisites/execution 설명 |
| 평가 기준 변경 | 새 rubric 버전 생성. v1 배점은 유지 |

## 001 대비 관찰

- QA/AI-QA base 계약 분리가 반영되었다.
- `qa-output` 커밋 정책 불일치가 해소되었다.
- runner 호출 조립부가 분리되었다.
- activation matrix 변환 규칙이 더 명확해졌다.
- minimal-core 예시가 추가되었다.
- 남은 주요 불일치는 activation guide의 reporter 경로와 runner adapter 문서화 수준이다.
