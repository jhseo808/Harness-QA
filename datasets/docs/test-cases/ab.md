# A/B 테스트 케이스 (A/B)

모델, 프롬프트, RAG 설정, Tool Calling 정책 변경이 실제 품질과 운영 지표에 미치는 영향을 비교하는 케이스입니다.

## 케이스 구조

```json
{
  "id": "ab-{category}-{seq:04d}",
  "version": "1.0.0",
  "dataset_version": "v1.0",
  "category": "prompt|model|rag_top_k|chunking|retrieval_filter|response_format|tool_policy",
  "ai_type": "generative|rag|agentic",
  "suite_tags": ["release", "nightly"],
  "risk_level": "P1|P2|P3",
  "status": "active",
  "variants": {
    "control": {
      "model_id": "...",
      "prompt_version": "...",
      "rag_config_version": "..."
    },
    "candidate": {
      "model_id": "...",
      "prompt_version": "...",
      "rag_config_version": "..."
    }
  },
  "input": {
    "user": "...",
    "context_documents": []
  },
  "expected": {
    "behavior": "candidate_not_worse_than_control",
    "evaluation_method": "llm_judge|human|schema|range_check",
    "pass_threshold": 0.8
  },
  "metrics": {
    "quality": ["accuracy", "groundedness", "format", "usefulness"],
    "safety": ["safety_violation_rate", "pii_exposure_count"],
    "product": ["user_satisfaction", "reask_rate", "answer_acceptance_rate", "error_report_rate"],
    "operations": ["p95_latency_ms", "cost_per_request_usd"]
  },
  "metadata": {
    "created_at": "ISO8601",
    "source": "human",
    "owner": "ai-qa"
  }
}
```

## 판정 원칙

- 안전성 위반률은 candidate가 control보다 좋아도 절대 기준을 통과해야 한다.
- 품질 지표가 상승해도 비용이나 지연이 SLA를 넘으면 조건부 또는 실패로 판정한다.
- RAG A/B는 동일 질문, 동일 문서 버전, 동일 권한 조건에서만 비교한다.
- 모델 A/B는 동일 dataset_version과 동일 rubric_version으로만 비교한다.

## 운영 지표

| 지표 | 의미 |
|------|------|
| `user_satisfaction` | 사용자 명시 피드백 또는 샘플링 리뷰 만족도 |
| `reask_rate` | 답변 후 재질문 또는 재시도 비율 |
| `answer_acceptance_rate` | 답변 채택, 복사, 해결 표시 등 성공 신호 |
| `error_report_rate` | 오류 신고, thumbs down, CS escalation 비율 |
| `safety_violation_rate` | 정책 위반 또는 안전 필터 실패율 |
