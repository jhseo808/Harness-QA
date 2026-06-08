# 사용자 피드백 기반 케이스 (Feedback)

운영 중 수집된 사용자 피드백을 회귀 테스트 자산으로 전환하는 영역입니다. 사용자 피드백은 실제 프로덕션 실패에서 나온 가장 강한 테스트 신호입니다.

## 케이스 구조

```json
{
  "id": "fb-{category}-{seq:04d}",
  "version": "1.0.0",
  "dataset_version": "v1.0",
  "category": "wrong_answer|bad_source|irrelevant|too_long|too_short|stale|format_error|unsafe|task_failure",
  "ai_type": "generative|rag|agentic",
  "suite_tags": ["release", "nightly"],
  "risk_level": "P0|P1|P2|P3",
  "status": "pending_review|reviewed|active|deprecated",
  "input": {
    "user": "사용자 원 질문",
    "context_documents": [],
    "conversation_history": []
  },
  "observed_output": {
    "response": "문제가 된 실제 응답",
    "source_documents": [],
    "model_id": "...",
    "prompt_version": "...",
    "rag_document_version": "..."
  },
  "expected": {
    "behavior": "correct_answer|grounded_answer|safe_refusal|format_compliance|task_completion",
    "evaluation_method": "llm_judge|human|exact_match",
    "pass_threshold": 0.8
  },
  "metadata": {
    "created_at": "ISO8601",
    "source": "production_feedback",
    "feedback_channel": "thumbs_down|support_ticket|cs_review|manual_triage",
    "occurrence_count": 1,
    "reviewed_by": "",
    "review_date": "",
    "owner": "ai-qa"
  }
}
```

## 승격 흐름

| 상태 | 의미 | 다음 단계 |
|------|------|-----------|
| `pending_review` | 원본 피드백이 수집됨 | 중복/재현 가능성/위험도 검토 |
| `reviewed` | QA가 문제 유형과 기대 동작을 확정 | release 또는 nightly suite 편입 |
| `active` | 회귀 테스트에서 실행 중 | 반복 실패 시 golden 후보 검토 |
| `deprecated` | 더 이상 유효하지 않은 케이스 | 이유와 대체 케이스 기록 |

## 분류 기준

- 답변이 틀림 → `capability` 또는 `hallucination/factual`
- 출처가 부정확함 → `hallucination/rag-grounding`
- 최신 정보가 아님 → `hallucination/rag-grounding`의 `stale_data`
- 위험하거나 부적절함 → `safety`
- 원하는 작업을 수행하지 못함 → `capability` 또는 `agent-specific`
- 형식이 맞지 않음 → `capability`의 format 케이스

## 원칙

- 원본 사용자 데이터는 필요한 범위만 보존하고 PII는 마스킹한다.
- 동일 이슈가 2회 이상 발생하면 release suite 편입을 검토한다.
- P0/P1 피드백은 단일 발생이어도 즉시 회귀 케이스 후보로 등록한다.
- 피드백 케이스를 golden으로 승격할 때는 사람이 기대 동작을 확정해야 한다.
