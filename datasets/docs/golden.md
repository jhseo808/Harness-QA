# 골든 데이터셋 (Golden Dataset)

회귀 평가의 기준이 되는 큐레이션된 테스트 케이스 컬렉션입니다.

## 목적

골든셋은 모델 버전 간 비교를 위한 **고정 기준점**입니다.
- 모델이 변경되면 반드시 동일한 골든셋으로 비교
- 골든셋 자체는 신중하게만 수정 (수정 시 이전 버전 결과와 비교 불가)
- 골든셋 버전 변경은 주요 이벤트로 관리 (`dataset_version` 변경)

## 케이스 구성 원칙

```
정상 케이스 (Normal)    50%  — 실제 서비스에서 빈번한 시나리오
경계 케이스 (Boundary)  20%  — 엣지 케이스, 긴 입력, 다국어
부정 케이스 (Negative)  20%  — 거부가 올바른 케이스
적대적 케이스 (Adversarial) 10% — 인젝션, Jailbreak 시도
```

## 케이스 구조

```json
{
  "id": "golden-{category}-{seq:04d}",
  "version": "1.0.0",
  "dataset_version": "v1.0",
  "category": "normal|boundary|negative|adversarial",
  "ai_type": "generative|rag|agentic",
  "input": {
    "system": "...",
    "user": "...",
    "context_documents": []
  },
  "expected": {
    "behavior": "...",
    "ground_truth": "...",
    "evaluation_rubric": "default|safety|alignment",
    "evaluation_method": "exact_match|llm_judge|human",
    "pass_threshold": 0.8
  },
  "metadata": {
    "created_at": "ISO8601",
    "source": "human",
    "reviewed_by": "human",
    "review_date": "ISO8601",
    "owner": "ai-qa",
    "tags": ["golden"]
  }
}
```

## dataset_version 관리

| 버전 | 변경 내용 | 변경일 |
|------|---------|-------|
| v1.0 | 초기 구성 | - |

**버전 변경 규칙:**
- 케이스 추가: 마이너 버전 업 (v1.0 → v1.1)
- 케이스 수정: 메이저 버전 업 (v1.x → v2.0) + 이전 버전 결과 보존
- 케이스 삭제: 메이저 버전 업 (삭제 이유 기록 필수)

## 베이스라인 결과 관리

골든셋 케이스 파일은 테스트 입력과 기대 동작만 보관합니다. 실행 결과는 케이스 파일에 누적하지 않고 `datasets/results/{model_id}/{dataset_version}/{run_id}/`에 append-only로 저장합니다.

릴리즈 후 기준선으로 승인된 집계만 `datasets/baselines/{model_version}/summary.json`에 저장합니다. baseline 승격은 `model-rollout-monitor` 또는 명시 승인된 단계에서만 수행합니다.
