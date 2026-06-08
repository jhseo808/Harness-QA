# 테스트 결과 저장소 (Results)

모든 AI QA 테스트 실행 결과를 버전별로 저장합니다.

## 디렉터리 구조

```
datasets/results/
  {model_version}/
    {dataset_version}/
      {run_id}/
        summary.json       — 실행 집계 결과
        cases/
          {case_id}.json   — 개별 케이스 결과
```

`run_id`는 매 실행마다 새로 발급합니다. 예: `run-20260608-001`.

**예시:**
```
datasets/results/
  claude-sonnet-4-6/
    v1.0/
      run-20260608-001/
        summary.json
        cases/
          golden-normal-0001.json
          golden-normal-0002.json
```

## 결과 파일 스키마

### 개별 케이스 결과 (`cases/{case_id}.json`)

```json
{
  "run_id": "run-{YYYYMMDD}-{seq:03d}",
  "case_id": "golden-normal-0001",
  "version_snapshot": {
    "model_id": "claude-sonnet-4-6",
    "model_version": "claude-sonnet-4-6-20250722",
    "algorithm_version": "v1",
    "dataset_version": "v1.0",
    "rubric_version": "1.0",
    "prompt_version": "system-v2.1"
  },
  "config": {
    "temperature": 0.0,
    "top_p": 1.0,
    "max_tokens": 2048,
    "environment": "staging"
  },
  "test_case": {
    "id": "golden-normal-0001",
    "category": "normal",
    "ai_type": "generative",
    "input_user": "...",
    "input_system": "..."
  },
  "output": {
    "response": "...",
    "latency_ms": 1250,
    "tokens_input": 150,
    "tokens_output": 300,
    "finish_reason": "end_turn"
  },
  "evaluation": {
    "method": "llm_judge",
    "judge_model": "claude-opus-4-8",
    "rubric_id": "default",
    "scores": {
      "accuracy": 0.9,
      "relevance": 1.0,
      "completeness": 0.8,
      "groundedness": null,
      "consistency": null,
      "safety": 1.0,
      "format": 1.0
    },
    "weighted_score": 0.92,
    "pass": true,
    "failure_reason": null
  },
  "executed_at": "ISO8601"
}
```

### 실행 집계 결과 (`summary.json`)

```json
{
  "run_id": "run-20260608-001",
  "version_snapshot": { "...": "..." },
  "executed_at": "ISO8601",
  "total_cases": 0,
  "passed": 0,
  "failed": 0,
  "pass_rate_pct": 0.0,
  "by_category": {
    "normal": {"total": 0, "passed": 0},
    "boundary": {"total": 0, "passed": 0},
    "negative": {"total": 0, "passed": 0},
    "adversarial": {"total": 0, "passed": 0}
  },
  "by_dimension": {
    "accuracy": {"mean": 0.0, "min": 0.0},
    "safety": {"mean": 0.0, "violations": 0}
  },
  "performance": {
    "latency_p50_ms": 0,
    "latency_p95_ms": 0,
    "latency_p99_ms": 0,
    "total_tokens_input": 0,
    "total_tokens_output": 0,
    "estimated_cost_usd": 0.0
  }
}
```

## 버전 비교 원칙

- **동일 `dataset_version` 비교만 유효**: dataset_version이 다른 결과는 직접 비교 불가
- `version_snapshot`이 없는 결과는 비교 대상에서 제외
- 결과 파일은 **Append-only**: 기존 결과 수정 금지, 재실행 시 새 `run_id` 사용

## 자동 저장 규칙

- 각 AI QA 에이전트는 테스트 완료 후 케이스별 결과를 이 경로에 저장
- `run_id` 형식: `run-{YYYYMMDD}-{seq:03d}` (당일 순번)
- `datasets/baselines/`에 집계 지표 동기화는 `model-rollout-monitor` 또는 명시 승인된 baseline 승격 단계만 담당
- 실행 결과는 baseline으로 자동 승격하지 않는다
