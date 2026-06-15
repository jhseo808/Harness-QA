# 하네스 구조 평가 프롬프트

사용자가 Harness-QA 구조 평가를 요청하면 이 프롬프트를 기준으로 평가한다.

## 목적

현재 프로젝트의 **하네스 방식과 구조**를 평가한다.
평가 대상은 테스트 결과나 output 산출물이 아니라, 여러 QA팀이 공통으로 사용할 수 있는 실행 방식, step 계약, agent 구조, 확장 경계, 온보딩/유지보수 구조다.
다른 QA팀이 이 하네스를 가져가서 README, docs, datasets 안내까지 수정하며 운영할 수 있으므로 해당 파일들도 하네스 구조의 일부로 평가한다.
이 평가는 하네스를 위한 QA다. 모델, agent, dataset, workflow가 계속 변경되어도 하네스의 핵심 계약과 평가 기준이 흔들리지 않는지 확인한다.

이 평가는 릴리스 판단이 아니라 구조 진단이다. 통과/실패 같은 이분법적 판정을 사용하지 않는다.

## 권장 평가자

하네스 구조 평가는 Codex로 수행하는 것을 권장한다.
대부분의 하네스 작성과 실행이 Claude Code 중심으로 이루어질 수 있으므로, 구조 평가는 다른 모델 계열로 분리해 자기평가 편향을 줄인다.
다른 모델을 사용해도 완전한 객관성이 자동으로 보장되지는 않으므로, 모든 판단은 루브릭과 실제 구조 근거에 묶어서 작성한다.

## 반드시 사용할 루브릭

먼저 아래 파일을 읽고 적용한다.

- `assessments/rubrics/harness-structure-rubric.v1.md`

v1 평가 중에는 루브릭 배점을 변경하지 않는다.
총점은 세부 점수 합계와 반드시 일치해야 한다.
첫 공식 run이 생성된 뒤에는 v1 루브릭의 배점과 평가 기준을 수정하지 않는다.
평가 기준을 바꿔야 하면 새 루브릭 버전 파일을 만든다.

## 반드시 검토할 하네스 구조 파일

점수 산정 전에 현재 프로젝트의 관련 구조 파일을 읽거나 확인한다.

- `scripts/execute.py`
- `.claude/commands/harness.md`
- `agents/qa/`
- `agents/ai-qa/`
- `agents/qa/_base.md`
- `agents/ai-qa/_base.md`
- `examples/phases/**/index.json`
- `examples/phases/**/step*.md`
- `datasets/manifest.yaml`
- `datasets/schemas/`
- `datasets/test-cases/`
- `datasets/README.md`
- `datasets/docs/`
- `README.md`
- `GETTING_STARTED.md`
- `docs/`
- `assessments/`

평가에서 제외한다.

- `scripts/test_execute.py`와 테스트 통과 여부
- `datasets/results/`
- `qa-output/`
- cache 디렉터리
- 특정 제품이나 프로젝트의 QA 산출물

문서류는 문장 품질이나 분량으로 평가하지 않는다.
다른 QA팀이 하네스를 도입하고 변경하고 확장할 때 필요한 구조적 안내가 있는지를 평가한다.

## 근거 수집 지침

명령 실행이나 파일 검토는 점수 근거로만 사용한다.
자동 검증 결과가 평가를 대신하지 않는다.

유용한 확인 항목:

- `scripts/execute.py`의 step 선택, 상태 전이, result 반영, agent 로드 구조
- `.claude/commands/harness.md`의 phase/index/step 생성 workflow
- `agents/qa/`와 `agents/ai-qa/`의 역할 분포, 역할 중복, 선택 확장 가능성
- `_base.md`와 개별 agent 파일의 공통 계약/개별 계약 분리, 입력/출력/금지사항/result 보고 구조
- `examples/phases/**/index.json`의 agent 지정과 step 순서
- `examples/phases/**/step*.md`의 하네스 계약 사용 패턴
- `datasets/manifest.yaml`과 `datasets/schemas/`가 AI-QA 확장 구조에 연결되는 방식
- `datasets/test-cases/`가 새 QA팀이 참고할 수 있는 seed/template 데이터로 구성되어 있는 방식
- `datasets/README.md`와 `datasets/docs/`가 dataset 운영과 확장 방식을 설명하는 방식
- `README.md`, `GETTING_STARTED.md`, `docs/`가 새 QA팀의 도입, 변경, 유지보수 경로를 안내하는 방식
- 모델 변경, agent 추가, dataset 확장, slash command 변경 시 함께 갱신되어야 할 계약과 문서가 드러나는 방식
- `assessments/`의 run 기반 평가 이력 구조
- 직전 run이 있다면 직전 run 이후 바뀐 하네스 구성 요소와 점수 영향
- 평가에 사용한 평가자 도구와 모델 계열

아래 항목은 점수 근거로 사용하지 않는다.

- `pytest` 실행 결과
- dataset test case의 자동 스키마 검증 결과
- `qa-output/`과 `datasets/results/`의 실제 산출물 품질

## 평가 Run 디렉터리

새 평가 디렉터리를 만든다.

```text
assessments/runs/assess-YYYYMMDD-NNN/
```

`YYYYMMDD`는 현재 로컬 날짜를 사용한다.
`NNN`은 같은 날짜의 다음 순번을 사용한다.

각 run은 아래 파일을 포함한다.

```text
assessment.json
report.md
snapshot.md
```

필요하면 근거 파일을 아래에 추가한다.

```text
evidence/
```

## assessment.json 형식

기계적으로 비교 가능한 요약을 작성한다.

```json
{
  "assessment_id": "assess-YYYYMMDD-NNN",
  "target": "harness-structure",
  "rubric_version": "harness-structure-rubric.v1",
  "evaluated_at": "YYYY-MM-DDTHH:MM:SS+09:00",
  "evaluator": {
    "tool": "Codex",
    "model_family": "unknown",
    "reason": "Claude Code 중심 하네스를 다른 모델 계열로 평가해 자기평가 편향을 줄이기 위함"
  },
  "harness_commit": "<git commit 또는 unknown>",
  "working_tree_state": "clean|dirty|unknown",
  "compared_to_run": "<previous assessment_id 또는 none>",
  "total_score": 0,
  "rating": "",
  "scores": {
    "core_execution_method": 0,
    "step_state_result_contract": 0,
    "qa_agent_structure": 0,
    "core_extension_boundary": 0,
    "onboarding_maintainability_structure": 0,
    "example_template_structure": 0,
    "assessment_history_structure": 0
  },
  "strengths": [],
  "risks": [],
  "change_impact_summary": [],
  "recommended_next_actions": [],
  "target_score": 95,
  "target_score_gap": 0,
  "priority_improvements_to_95": [],
  "evidence_files": []
}
```

모든 숫자 점수의 합은 `total_score`와 정확히 일치해야 한다.
`target_score_gap`은 `max(95 - total_score, 0)`으로 계산한다.
총점이 95점 미만이면 `priority_improvements_to_95`에 95점 이상을 목표로 필요한 보완 항목을 우선순위대로 작성한다.

`priority_improvements_to_95` 항목은 아래 형식을 따른다.

```json
{
  "priority": "P0",
  "item": "개선 항목",
  "rubric_area": "관련 루브릭 영역",
  "expected_score_gain": 0,
  "difficulty": "low|medium|high",
  "reason": "왜 먼저 처리해야 하는지",
  "suggested_change": "수정 또는 보완 방향"
}
```

## report.md 형식

아래 구조를 사용한다.

```markdown
# 하네스 구조 평가: assess-YYYYMMDD-NNN

## 요약

| 항목 | 내용 |
|---|---|
| 평가일 | YYYY-MM-DD |
| 루브릭 | harness-structure-rubric.v1 |
| 하네스 커밋 | <commit> |
| 평가자 | Codex / <model_family> |
| 비교 대상 | <previous assessment_id 또는 none> |
| 점수 | NN / 100 |
| 등급 | <점수 등급> |

## 핵심 판단

현재 하네스 구조에 대한 짧고 명확한 판단.

## 점수 상세

| 영역 | 점수 | 근거 |
|---|---:|---|

## 주요 강점

## 구조적 리스크

## Core/확장 경계 검토

## Agent 구조 검토

## 온보딩/유지보수 구조 검토

## 모델/하네스 변경 내성 검토

## 이전 평가 대비 변경 사항

직전 run이 없으면 "첫 run이므로 비교 대상 없음"이라고 적는다.
직전 run이 있으면 주요 변경 파일과 점수 영향 가능성을 적는다.

## 평가자/모델 기록

평가에 사용한 도구, 모델 계열, Codex 사용 이유를 적는다.

## 개선 우선순위

## 95점 목표 개선안

현재 점수가 95점 미만이면 이 섹션을 반드시 작성한다.

| 우선순위 | 개선 항목 | 관련 영역 | 예상 점수 개선 | 난이도 | 이유 | 제안 수정 |
|---|---|---|---:|---|---|---|

## 근거
```

## snapshot.md 형식

평가 당시 구조를 요약한다.

- Git commit과 working tree 상태
- 평가자 도구와 모델 계열
- 직전 run ID와 비교 여부
- 검토한 핵심 구조 파일
- agent 그룹별 개수
- example phase와 step 구성
- AI-QA 확장 연결 구조
- README/GETTING_STARTED/docs/datasets 안내 구조
- 모델/agent/dataset/workflow 변경 시 갱신 경계
- assessments 구조 요약

## 이력 갱신

평가 run 작성 후 아래를 갱신한다.

- `assessments/history.md`에 평가 이력을 한 줄 추가한다.
- `assessments/latest.md`를 최신 run을 가리키도록 수정한다.
- `history.md`에는 평가자, 비교 대상 run, 주요 변경 영향도 함께 남긴다.

`assessments/legacy/` 아래의 과거 평가 기록은 수정하지 않는다.
필요하면 리포트에서 과거 평가 기록이라고만 언급한다.

## 점수 산정 태도

- 테스트 통과 여부나 output 품질로 점수를 주지 않는다.
- 하네스가 크다는 이유만으로 높은 점수를 주지 않는다.
- 작은 Core, 명확한 step 계약, agent 역할 분리, 선택 가능한 확장 경로, 유지보수 가능한 안내 구조를 높게 평가한다.
- agent 역할 중복, Core와 AI-QA 경계 흐림, 실행기와 확장 구조의 결합도는 감점한다.
- README/docs/datasets는 문장 품질이 아니라 새 QA팀이 하네스를 바꾸고 유지할 수 있게 하는 구조적 안내로 평가한다.
- 모델이 바뀌어도 같은 하네스 계약으로 실행, 기록, 평가할 수 있는지를 중요하게 본다.
- 하네스 파일이 바뀔 때 루브릭과 예시와 문서가 함께 갱신될 수 있는 구조인지 확인한다.
- 직전 평가와 비교하지 못했다면 비교하지 못한 이유를 적는다.
- 평가자 도구와 모델 계열을 기록해 이후 평가 편차를 해석할 수 있게 한다.
- 근거를 지어내지 않는다. 불확실하면 불확실성을 적고 보수적으로 평가한다.
