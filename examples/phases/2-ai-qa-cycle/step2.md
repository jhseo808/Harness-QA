# Step 2: rag-pipeline-test (RAG Pipeline Tester)

## 컨텍스트

이전 step 산출물:
- `qa-output/ai-qa-strategy.md` — RAG 파이프라인 구성 정보
- `qa-output/ai-eval-setup.md` — 평가 루브릭 (참조)

**이번 사이클의 RAG 변경 사항:**
- 청킹 전략 변경: 500토큰 → 300토큰 청크 크기
- 문서 컬렉션 업데이트: 환불 정책 개정, 신규 제품 설명 추가

## 작업

변경된 RAG 파이프라인의 각 단계를 검증하라.

**집중 검증 영역 (변경 사항 기반):**

1. **청킹 품질** (이번 사이클 최우선)
   - 500→300 토큰 변경 후 경계 무결성 확인
   - 특히 표, 절차 설명, 코드 블록이 포함된 제품 설명 문서 검수
   - 너무 짧은 청크(< 50토큰)가 과도하게 생성되었는지 확인

2. **인덱싱 동기화**
   - 개정된 환불 정책 문서가 검색 가능한지 확인
   - 구버전 환불 정책이 여전히 검색되지 않는지 확인

3. **Vector DB 성능**
   - 청크 크기 변경 후 검색 지연 시간 기준(100ms) 유지 확인

**테스트 문서:** 환불 정책 문서(신구 버전), 제품 설명 문서(표 포함), 설치 가이드(절차 포함)

## Acceptance Criteria

- `qa-output/rag-pipeline-result.md` 존재 및 다음 포함:
  - 청킹 경계 오류 건수 (0건 목표)
  - 신규 문서 인덱싱 확인
  - 구버전 문서 노출 건수 (0건 목표)
  - Vector DB 검색 지연 P95 (100ms 이내)
- `qa-output/rag-pipeline-summary.json` — 구조화 요약
- 청킹 경계 오류 또는 구버전 노출이 있으면 `release_gate: fail`

## 결과 파일 작성

작업 완료 후 `examples/phases/2-ai-qa-cycle/step2-result.json`을 작성하라:
- 성공 → `{"status": "completed", "summary": "RAG 파이프라인 검증 완료. 청킹 오류: 0건, 인덱싱: 정상, 검색 지연 P95: 78ms", "artifacts": ["qa-output/rag-pipeline-result.md", "qa-output/rag-pipeline-summary.json"]}`
- 결함 발견 → `{"status": "completed", "summary": "RAG 파이프라인 검증 완료. 청킹 경계 오류 3건 발견 (표 분리)", "artifacts": ["qa-output/rag-pipeline-result.md", "qa-output/rag-pipeline-summary.json"]}`
- 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`
