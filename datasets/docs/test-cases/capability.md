# 역량 평가 테스트 케이스 (Capability)

모델의 핵심 기능 수행 능력을 평가하는 케이스입니다.

## 케이스 구조

```json
{
  "id": "cap-{category}-{seq:04d}",
  "version": "1.0.0",
  "dataset_version": "v1.0",
  "category": "qa|summarization|translation|code|classification|reasoning",
  "ai_type": "generative|rag|agentic",
  "suite_tags": ["release", "nightly"],
  "risk_level": "P1|P2|P3",
  "status": "active",
  "difficulty": "basic|intermediate|advanced",
  "input": {
    "system": "...",
    "user": "...",
    "context": "..."
  },
  "expected": {
    "behavior": "정답 포함 | 형식 준수 | 거부",
    "ground_truth": "...",
    "evaluation_method": "exact_match|rouge|llm_judge|human",
    "pass_threshold": 0.8
  },
  "metadata": {
    "created_at": "ISO8601",
    "source": "human",
    "domain": "general|medical|legal|finance|tech",
    "language": "ko|en|multi",
    "tags": []
  }
}
```

## 카테고리별 구성 비율

| 카테고리 | 비율 | 설명 |
|---------|------|------|
| Q&A | 30% | 사실 기반 질의응답 |
| 요약 | 20% | 문서/대화 요약 |
| 번역 | 15% | 언어 간 번역 |
| 코드 | 20% | 코드 생성/수정/설명 |
| 추론 | 15% | 논리/수학적 추론 |

## 골든셋 구분

- `golden: true` 태그가 있는 케이스는 `datasets/golden/`에도 동기화됨
- 골든셋 수정 시 두 위치 모두 업데이트 필요

## 추가 가이드

- 케이스 ID는 영구 고유값 — 수정 시 새 ID 발급, 기존 ID 삭제 금지
- `ground_truth`가 있는 케이스만 자동 평가 가능
- 없는 케이스는 `evaluation_method: llm_judge` 또는 `human` 사용
