# 모델 베이스라인 (Baselines)

모델 버전별 프로덕션 집계 지표를 저장합니다. 다음 모델 변경 시 회귀 비교 기준이 됩니다.

## 디렉터리 구조

```
datasets/baselines/
  {model_version}/
    summary.json       — 해당 모델의 집계 지표
    by_category.json   — 카테고리별 세분화 지표
```

## `summary.json` 스키마

```json
{
  "model_version": "claude-sonnet-4-6-20250722",
  "model_id": "claude-sonnet-4-6",
  "dataset_version": "v1.0",
  "baseline_date": "ISO8601",
  "source": "staging|production",
  "sample_size": 0,

  "quality": {
    "overall_pass_rate_pct": 0.0,
    "accuracy_mean": 0.0,
    "relevance_mean": 0.0,
    "completeness_mean": 0.0,
    "groundedness_mean": 0.0,
    "consistency_mean": 0.0,
    "format_compliance_pct": 0.0
  },

  "safety": {
    "harmful_content_rate_pct": 0.0,
    "jailbreak_success_rate_pct": 0.0,
    "pii_exposure_count": 0,
    "safety_violations_total": 0
  },

  "alignment": {
    "sycophancy_rate_pct": 0.0,
    "overconfidence_rate_pct": 0.0,
    "honesty_score_mean": 0.0
  },

  "performance": {
    "latency_p50_ms": 0,
    "latency_p95_ms": 0,
    "latency_p99_ms": 0,
    "tokens_per_request_input_mean": 0,
    "tokens_per_request_output_mean": 0,
    "cost_per_request_usd_mean": 0.0
  },

  "hallucination": {
    "factual_hallucination_rate_pct": 0.0,
    "reference_hallucination_rate_pct": 0.0,
    "rag_grounding_failure_rate_pct": 0.0
  }
}
```

## 베이스라인 갱신 규칙

1. **새 모델 배포 완료** → `model-rollout-monitor`가 30일 평균 지표 저장
2. **기존 베이스라인 수정 금지** — 새 디렉터리에 저장, 이전 버전 유지
3. **dataset_version 변경 시** — 동일 모델이라도 새 베이스라인 생성

## 비교 사용법

모델 변경 QA 시 `model-capability-evaluator`가 이 파일을 읽어 회귀 여부를 판단합니다.

```
비교 절차:
1. 신규 모델로 동일 dataset_version 골든셋 실행
2. datasets/baselines/{이전 모델}/summary.json 로드
3. 각 지표를 허용 임계값과 비교
4. 초과 시 릴리즈 차단
```

## 보존 정책

- 모든 이전 버전 베이스라인 영구 보존
- 비교 가능성을 위해 삭제 금지
- 저장 공간 문제 시 오래된 버전은 별도 아카이브로 이동
