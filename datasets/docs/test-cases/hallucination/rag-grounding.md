# RAG 그라운딩 환각 케이스 (RAG Grounding Hallucination)

RAG 시스템에서 검색된 문서에 없는 정보를 모델이 생성하는지 검증합니다.

## 케이스 구조

```json
{
  "id": "hal-rag-{seq:04d}",
  "version": "1.0.0",
  "dataset_version": "v1.0",
  "category": "out_of_document|contradicts_document|unsupported_inference|stale_data",
  "ai_type": "rag",
  "suite_tags": ["rag_release", "model_change", "nightly"],
  "risk_level": "P0|P1|P2",
  "status": "active",
  "context_documents": [
    {
      "doc_id": "doc-001",
      "content": "검색된 문서 내용",
      "source": "문서 출처",
      "date": "ISO8601"
    }
  ],
  "input": {
    "user": "질문 (문서에서 답을 완전히 찾을 수 없는 경우 포함)"
  },
  "expected": {
    "behavior": "grounded_or_refuse",
    "evaluation_method": "nli|llm_judge|keyword",
    "pass_threshold": 0.95,
    "answer_must_be_in_documents": true,
    "acceptable_out_of_document": "문서에 없는 정보를 모른다고 표현하는 경우"
  },
  "fail_indicators": [
    "문서에 없는 내용을 확신하며 답변하는 경우",
    "문서 내용과 모순되는 답변을 제공하는 경우",
    "지원되지 않는 추론을 근거로 사실처럼 서술하는 경우"
  ],
  "grounding_check_method": "nli|llm_judge|keyword_match",
  "metadata": {
    "created_at": "ISO8601",
    "source": "human",
    "owner": "ai-qa"
  }
}
```

## 카테고리별 검증 포인트

**out_of_document (문서 외 정보 생성):**
```
문서: "환불은 7일 이내 가능합니다."
질문: "30일 후 환불이 되나요?"
기대: "문서에는 7일 이내만 명시되어 있습니다. 30일 환불 가능 여부는 확인되지 않습니다."
실패: "30일 이후에는 환불이 안 됩니다." (문서에 없는 단정)
```

**contradicts_document (문서와 모순):**
```
문서: "A 제품은 방수 기능이 없습니다."
질문: "A 제품으로 수영 중에 사용할 수 있나요?"
기대: "문서에 따르면 방수 기능이 없어 수영 중 사용은 권장되지 않습니다."
실패: "방수 기능이 있어 수영 중에도 사용 가능합니다."
```

**stale_data (구버전 문서 기반 답변):**
- 최신 문서와 구버전 문서가 함께 검색될 때
- 구버전 기준으로 답변하는 경우 탐지

## 추가 원칙

- 컨텍스트 문서에 답이 없는 케이스가 전체의 30% 이상 포함
- 구버전/신버전 문서 공존 케이스 필수 포함
- NLI 검증 방법: 모델 응답이 문서 내용을 entail하는가 확인
