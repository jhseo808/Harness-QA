# Activation Matrix → Step 변환 가이드

`ai-qa-lead`가 생성하는 `qa-output/activation-matrix.json`을 후속 step 파일로 변환하는 방법을 설명합니다.

---

## activation-matrix.json 구조

`ai-qa-lead`는 변경 유형과 위험도에 따라 실행할 에이전트를 선택하고 아래 형식으로 기록합니다.
형식은 `datasets/schemas/activation-matrix.schema.json`을 따릅니다.

```json
{
  "cycle_name": "2-ai-qa-cycle",
  "dataset_version": "v1.0",
  "suite": "rag_release",
  "run_id": "run-20260613-001",
  "agents": [
    { "agent": "ai-qa/rag-pipeline-tester",          "status": "required", "reason": "RAG 파이프라인 청킹 변경",    "parallel_group": "service", "blocking_gate": null },
    { "agent": "ai-qa/rag-retrieval-tester",          "status": "required", "reason": "문서 컬렉션 업데이트",        "parallel_group": "service", "blocking_gate": null },
    { "agent": "ai-qa/ai-perf-observability-tester",  "status": "required", "reason": "응답 시간 SLA 검증",          "parallel_group": "service", "blocking_gate": null },
    { "agent": "ai-qa/ai-safety-tester",              "status": "required", "reason": "안전성 게이트 (항상 실행)",   "parallel_group": "final",   "blocking_gate": null },
    { "agent": "ai-qa/reporter",                      "status": "required", "reason": "종합 보고",                   "parallel_group": "final",   "blocking_gate": null }
  ]
}
```

`parallel_group` 허용값: `"setup"` | `"service"` | `"final"` | `"model"` | `"none"`

---

## Step 변환 절차

### 1단계: matrix 파일 열기

```bash
cat qa-output/activation-matrix.json
```

`agents` 목록에서 `status: "required"` 항목만 추출합니다. `status: "skipped"` 항목은 step으로 만들지 않습니다.

### 2단계: layer 순서로 step 번호 부여

| Layer | 의미 | step 번호 |
|-------|------|----------|
| 0 | 전략 수립 (ai-qa-lead) | step0 |
| 1 | 도메인 검증 (rag-pipeline, rag-retrieval 등) | step1, step2, … |
| 2 | 교차 검증 (perf, alignment 등) | 이전 layer 다음 번호 |
| 3 | 안전성 게이트 (ai-safety-tester) | 항상 layer 2 다음 |
| 4 | 종합 보고 (reporter) | 항상 마지막 |

같은 `parallel_group`에 속한 에이전트는 논리적으로 동시 실행이 가능하지만, **현재 execute.py는 순차 실행만 지원합니다.** 같은 그룹은 연속된 번호로 배정합니다.

### 3단계: step 파일 작성

각 step 파일은 D-3 템플릿 형식(`/harness` 커맨드 참고)을 따릅니다.

```markdown
# Step N: {에이전트 역할명}

## 컨텍스트

이전 step 산출물:
- `qa-output/{이전-agent-산출물}` — 설명

## 작업

{에이전트 페르소나 파일(agents/ai-qa/{agent}.md) 참고하여 작업 내용 기술}

## Acceptance Criteria

- `qa-output/{this-agent}-result.md` 존재 및 …
- `qa-output/{this-agent}-summary.json` 존재 및 `release_gate` 필드 포함

## 검증 절차

1. Acceptance Criteria를 모두 충족했는지 확인한다.
2. 작업 완료 후 `phases/{phase}/step{N}-result.json`을 작성하라.

## 금지사항

- {에이전트별 주요 금지사항}
```

### 4단계: index.json에 step 등록

```json
{
  "project": "my-project",
  "phase": "2-ai-qa-cycle",
  "steps": [
    { "step": 0, "name": "ai-qa-lead",           "status": "pending", "agent": "ai-qa/ai-qa-lead" },
    { "step": 1, "name": "rag-pipeline-tester",  "status": "pending", "agent": "ai-qa/rag-pipeline-tester" },
    { "step": 2, "name": "rag-retrieval-tester", "status": "pending", "agent": "ai-qa/rag-retrieval-tester" },
    { "step": 3, "name": "ai-perf-tester",       "status": "pending", "agent": "ai-qa/ai-perf-observability-tester" },
    { "step": 4, "name": "ai-safety-tester",     "status": "pending", "agent": "ai-qa/ai-safety-tester" },
    { "step": 5, "name": "reporter",             "status": "pending", "agent": "ai-qa/reporter" }
  ]
}
```

---

## 변환 예시: 경량 RAG 릴리스

변경 사항: 시스템 프롬프트 수정만 (파이프라인 변경 없음)

`ai-qa-lead`가 rag-pipeline-tester를 `status: "skipped"`로 표시한 경우 → step에서 제외:

| parallel_group | agent | status | → step |
|---|---|---|---|
| setup | ai-qa-lead | required | step0 |
| service | rag-pipeline-tester | **skipped** | 제외 |
| service | rag-retrieval-tester | required | step1 |
| service | gen-quality-tester | required | step2 |
| final | ai-safety-tester | required | step3 |
| final | reporter | required | step4 |

총 5개 step (기본 7개 대비 2개 절약).

---

## 향후 개선 방향

현재 execute.py는 순차 실행만 지원합니다. 같은 `parallel_group` 내 에이전트를 병렬 실행하는 `--parallel` 모드는 장기 로드맵에 있습니다. 병렬화가 필요한 경우 별도 터미널에서 phase를 분리해 실행하는 방법으로 우회할 수 있습니다.
