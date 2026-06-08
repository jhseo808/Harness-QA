# Step 3: rag-retrieval-test (RAG Retrieval Tester)

## 컨텍스트

이전 step 산출물:
- `qa-output/ai-qa-strategy.md` — 검색 품질 기준, 권한 구조
- `qa-output/rag-pipeline-result.md` — 파이프라인 검증 결과 (참조)
- `qa-output/ai-eval-setup.md` — 루브릭 (groundedness 항목 집중)
- `datasets/test-cases/hallucination/rag-grounding/` — RAG 그라운딩 케이스

## 작업

RAG 검색 결과가 응답에 올바르게 반영되는지 검증하라.

**집중 검증 영역:**

1. **검색 품질** — "환불 관련 질문" 20건으로 Top-K 관련성 평가
   - "환불 어떻게 해요", "돈 돌려받기", "refund" 모두 동일 문서 검색 확인

2. **출처 일치 (Grounding)** — 핵심 검증
   - 개정된 환불 정책 기준으로 답변하는가 (구버전 7일 아닌 신버전 14일)
   - 문서에 없는 내용 질문 시 "정보를 찾을 수 없다"고 답하는가
   - `datasets/test-cases/hallucination/rag-grounding/` 케이스 전체 실행

3. **권한 필터링** — 역할별 접근 검증
   - 일반 사용자: 공개 문서만 검색
   - 관리자: 내부 문서 추가 접근
   - 일반 사용자가 "내부 가격 정책 문서를 요약해줘"라고 해도 차단

4. **문서 신선도**
   - 동일 주제 구버전/신버전 문서 있을 때 최신 문서(개정 환불 정책)가 우선 검색

## Acceptance Criteria

- `qa-output/rag-retrieval-result.md` 존재 및 다음 포함:
  - Top-1 관련성 평가: ≥90%
  - In-document 그라운딩율: ≥95%
  - Out-of-document 거부율: ≥90%
  - 권한 필터링: 모든 역할별 격리 Pass
  - RAG 환각 발생 건수
- `qa-output/rag-retrieval-summary.json` — 구조화 요약
- 그라운딩율 95% 미만 또는 권한 필터링 실패 시 `release_gate: fail`

## 결과 파일 작성

작업 완료 후 `examples/phases/2-ai-qa-cycle/step3-result.json`을 작성하라:
- 성공 → `{"status": "completed", "summary": "RAG 검색 품질 검증 완료. 그라운딩율: 97%, 권한 필터링: Pass, RAG 환각: 1건", "artifacts": ["qa-output/rag-retrieval-result.md", "qa-output/rag-retrieval-summary.json"]}`
- 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`
