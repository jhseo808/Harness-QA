# 하네스 구조 평가

이 디렉터리는 Harness-QA 템플릿 자체의 구조 평가를 기록한다.
평가 대상은 특정 QA 결과, 모델 응답, 제품 릴리스가 아니라 **하네스 구조**다.
다른 QA팀이 하네스를 가져가서 수정하고 운영할 수 있어야 하므로 README, GETTING_STARTED, docs, datasets 안내 구조도 평가 범위에 포함한다.
즉, 이 평가는 **하네스를 위한 QA**다.
모델, agent, dataset, workflow, 문서가 계속 바뀌더라도 하네스의 핵심 계약이 유지되는지 확인한다.

핵심 질문은 다음과 같다.

> 이 하네스가 여러 QA팀이 가져다 쓰기에 가볍고, 명확하고, 유지보수 가능하며, 확장 가능한 구조인가?

## 현재 평가 체계

새 평가부터는 아래 파일을 기준으로 한다.

- 루브릭: `assessments/rubrics/harness-structure-rubric.v1.md`
- 평가 프롬프트: `assessments/templates/harness-assessment-prompt.md`
- 평가 결과 위치: `assessments/runs/assess-YYYYMMDD-NNN/`

기존 `index.md`, `v1.x.md` 파일은 `assessments/legacy/`에 보관된 과거 평가 기록이다.
역사적 맥락으로 유지하되, 새 평가는 run 기반 구조를 사용한다.

## 평가 원칙

- 하네스 구조 평가는 Codex로 수행하는 것을 권장한다.
- 대부분의 하네스 실행과 작성은 Claude Code를 사용할 수 있으므로, 구조 평가는 다른 모델 계열로 분리해 평가자 편향을 줄인다.
- 다른 모델을 쓴다고 완전한 객관성이 보장되는 것은 아니지만, 같은 도구가 자기 구조를 평가하는 상황보다 더 독립적인 관찰을 기대할 수 있다.
- 통과/실패 같은 이분법적 판정을 하지 않는다.
- 릴리스 판단을 하지 않는다.
- 하네스 구조, 확장 구조, 온보딩/유지보수 구조를 평가한다.
- 100점 고정 루브릭을 사용한다.
- 총점은 세부 점수의 합계와 반드시 일치해야 한다.
- 루브릭 밖의 홀리스틱 보정점은 사용하지 않는다.
- 95점 이상은 목표 성숙도이지 강제 조건이 아니다.
- 첫 공식 run이 생성된 뒤에는 해당 루브릭 버전의 배점과 평가 기준을 변경하지 않는다.
- 평가 기준을 바꿔야 하면 기존 파일을 고치지 않고 새 루브릭 버전을 만든다.
- 평가 근거는 나중에 다시 검토할 수 있도록 파일 경로와 관찰 내용으로 남긴다.
- 기능이 많은 하네스보다, 작고 명확한 Core와 선택 가능한 확장 구조를 더 높게 평가한다.
- README/docs/datasets는 문장 품질이 아니라 다른 QA팀이 하네스를 도입, 변경, 확장할 수 있게 하는 구조적 안내로 평가한다.
- 테스트 스크립트, 테스트 통과 여부, `qa-output/`, `datasets/results/`, 실제 QA 산출물 같은 output 내용은 평가에서 제외한다.
- 모델 변경, agent 추가, dataset 확장, slash command 변경 이후에도 같은 루브릭으로 구조를 다시 점검할 수 있어야 한다.
- 하네스가 변경될 때 함께 갱신해야 할 문서, 예시, 평가 기준이 드러나는 구조를 높게 평가한다.
- 평가 run에는 평가자 도구, 모델 계열, 직전 run 대비 변경 영향도 함께 기록한다.

## 평가 요청 방법

자연어로 다음처럼 요청하면 된다.

```text
assessments/templates/harness-assessment-prompt.md 기준으로
현재 하네스 구조를 평가해줘.
루브릭은 assessments/rubrics/harness-structure-rubric.v1.md를 사용하고,
결과는 새 assessments/runs/assess-YYYYMMDD-NNN/에 남겨줘.
```

권장 평가자는 Codex다. Claude Code로 하네스를 작성하고 실행하더라도, 구조 평가는 Codex에게 맡겨 다른 관점에서 점검하는 흐름을 기본으로 한다.

평가자는 먼저 루브릭을 읽고, 현재 프로젝트 파일을 검토한 뒤, 새 run 디렉터리에 `report.md`, `assessment.json`, `snapshot.md`를 작성한다.

## 평가 결과 구조

각 평가 run은 아래 파일을 포함한다.

```text
assessments/runs/assess-YYYYMMDD-NNN/
├── assessment.json
├── report.md
└── snapshot.md
```

필요하면 근거 파일을 추가할 수 있다.

```text
evidence/
├── structure-notes.md
├── onboarding-maintenance-notes.md
├── extension-boundary-notes.md
└── change-resilience-notes.md
```

## 이력 관리

평가 run을 만들 때마다 `assessments/history.md`에 한 줄을 추가한다.
`assessments/latest.md`는 가장 최근 평가 run을 가리키도록 갱신한다.
직전 run이 있으면 이번 평가가 어떤 변경 이후의 평가인지 함께 기록한다.

## 레거시 기록

과거 평가 기록은 아래 위치에 둔다.

```text
assessments/legacy/
├── index.md
├── v1.0.md
├── v1.1.md
├── v1.2.md
├── v1.3.md
└── v1.4.md
```

이 파일들은 새 루브릭 체계의 입력으로 자동 사용하지 않는다. 필요할 때 비교 맥락으로만 참고한다.
