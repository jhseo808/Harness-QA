# 평가 스냅샷: assess-20260614-001

## 기본 정보

| 항목 | 내용 |
|---|---|
| 평가 시각 | 2026-06-14T00:03:06+09:00 |
| 루브릭 | harness-structure-rubric.v1 |
| 평가자 | Codex / GPT-5 |
| Git commit | bb0d794 |
| Working tree | dirty |
| 비교 대상 | none |

첫 run이므로 직전 run 비교는 수행하지 않았다. 기존 `assessments/legacy/` 기록은 역사적 맥락으로만 참고했다.

## 검토한 핵심 구조

- `scripts/execute.py`
- `.claude/commands/harness.md`
- `agents/qa/`, `agents/ai-qa/`
- `agents/qa/_base.md`, `agents/ai-qa/_base.md`
- `examples/phases/**/index.json`, `examples/phases/**/step*.md`
- `datasets/manifest.yaml`
- `datasets/schemas/`
- `datasets/test-cases/`
- `datasets/README.md`, `datasets/docs/`
- `README.md`, `GETTING_STARTED.md`, `docs/`
- `assessments/`

평가에서 `scripts/test_execute.py`, 테스트 실행 결과, `qa-output/`, `datasets/results/`, 실제 QA 산출물 품질은 제외했다.

## 구조 수량

| 항목 | 수량 |
|---|---:|
| `agents/qa/*.md` | 11 |
| `agents/ai-qa/*.md` | 22 |
| `datasets/schemas/*.json` | 4 |
| `datasets/test-cases/**/*.json` | 56 |
| `examples/phases/**/step*.md` | 18 |

## 예시 phase 구성

| phase | 구조 |
|---|---|
| `0-mvp` | 일반 개발 흐름. step0~step3은 completed 예시, step4는 `qa/playwright` pending 예시 |
| `1-qa-cycle` | `qa/qa-lead` → requirements → test-case → api → playwright → reporter |
| `2-ai-qa-cycle` | `ai-qa/ai-qa-lead` → ai-evaluator → rag-pipeline → rag-retrieval → perf → safety → `qa/reporter` |

## 주요 관찰

- `scripts/execute.py`는 step 선택, 상태 전이, result 검증, 재시도, 복구, agent 주입, commit 분리를 단일 실행 루프로 제공한다.
- `.claude/commands/harness.md`는 phase/index/step 생성 계약과 agent 목록, activation matrix 수동 변환 방식을 설명한다.
- `README.md`와 `GETTING_STARTED.md`는 새 QA팀의 초기 도입 경로를 제공한다.
- `datasets/manifest.yaml`은 schema, rubric, case collection, suite, result storage, promotion policy를 연결한다.
- `docs/ACTIVATION_MATRIX_GUIDE.md`는 activation matrix를 step으로 변환하는 수동 절차를 제공한다.

## 변경 내성 관찰

- 모델 변경 검증을 위한 `model-*` agent와 dataset result storage 구조가 존재한다.
- 그러나 Core 실행기는 Claude CLI 호출에 직접 묶여 있어 모델/도구 호출부 adapter 경계가 약하다.
- activation matrix는 전략 문서로 정의되어 있고 실행기는 자동으로 읽지 않으므로, AI-QA 확장은 수동 변환 절차에 의존한다.
- `qa/_base.md`에 AI-QA 산출물 표가 함께 포함되어 일반 QA와 AI-QA 확장 경계가 완전히 분리되어 있지는 않다.

## 평가 이력 구조

- `assessments/rubrics/harness-structure-rubric.v1.md`로 고정 루브릭을 정의했다.
- `assessments/templates/harness-assessment-prompt.md`로 자연어 평가 절차와 산출물 형식을 정의했다.
- `assessments/legacy/`에 과거 v1.x 평가 기록이 분리되어 있다.
- 이 run부터 `assessments/runs/assess-YYYYMMDD-NNN/` 구조를 사용한다.
