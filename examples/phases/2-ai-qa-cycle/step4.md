# Step 4: perf-test (AI Perf & Observability Tester)

## 컨텍스트

이전 step 산출물:
- `qa-output/ai-qa-strategy.md` — 성능 기준 (P95 지연, 비용 한도)
- `qa-output/rag-pipeline-result.md` — 청킹 변경 결과 (검색 지연 영향 확인)
- `qa-output/rag-retrieval-summary.json` — 검색 품질 결과

**이번 사이클의 성능 관련 변경 사항:**
- 청킹 전략 변경: 500토큰 → 300토큰 (청크 수 증가 → Vector DB 검색 부하 증가 가능)
- 시스템 프롬프트 v2.0 → v2.1 (응답 길이 변화 → 토큰 비용 영향 가능)

## 작업

RAG 챗봇의 성능과 관측 가능성을 검증하라.

**집중 검증 영역:**

1. **응답 지연 (End-to-End)**
   - 기준: P95 ≤ 2000ms (사용자 체감 기준)
   - 청킹 변경 전후 지연 비교 (`datasets/results/`의 이전 run 또는 승인된 baseline과 비교)
   - Vector DB 검색 지연: P95 ≤ 100ms (rag-pipeline-result.md 값 확인)

2. **토큰 비용**
   - 프롬프트 v2.1 기준 평균 입출력 토큰 수 측정
   - v2.0 대비 비용 변화율 (%): ±10% 이내가 기준

3. **로그 가시성**
   - 모든 RAG 검색 쿼리 로그 확인 (소스 문서 ID 포함)
   - 오류 응답(에러율) 측정: ≤ 0.1%

4. **재현성**
   - temperature=0 설정 시 동일 쿼리에 동일 응답 확인 (3회 반복)

## Acceptance Criteria

- `qa-output/ai-perf-result.md` 존재 및 다음 포함:
  - E2E P95 지연 측정값 및 기준 충족 여부
  - Vector DB 검색 P95 (rag-pipeline과 교차 검증)
  - 토큰 비용 v2.0 대비 변화율
  - 에러율 측정값
- `qa-output/ai-perf-summary.json` — 구조화 요약
- P95 지연 > 2000ms 또는 비용 증가 > +10%이면 `release_gate: conditional`

## 결과 파일 작성

작업 완료 후 `examples/phases/2-ai-qa-cycle/step4-result.json`을 작성하라:
- 성공 → `{"status": "completed", "summary": "성능 검증 완료. E2E P95: 1240ms, Vector DB P95: 78ms, 토큰 비용 변화: +3%, 에러율: 0%", "artifacts": ["qa-output/ai-perf-result.md", "qa-output/ai-perf-summary.json"]}`
- 조건부 → `{"status": "completed", "summary": "성능 검증 완료. E2E P95: 1850ms (기준 근접). release_gate: conditional", "artifacts": ["qa-output/ai-perf-result.md", "qa-output/ai-perf-summary.json"]}`
- 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`
