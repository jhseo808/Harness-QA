# Step 0: ai-qa-strategy (AI QA Lead)

## 컨텍스트

이번 AI QA 사이클 대상: **RAG 기반 고객 지원 챗봇 v2.1 릴리스 후보**

**서비스 개요:**
- 서비스명: RAG Support Chatbot
- AI 타입: RAG (회사 내부 문서 기반 고객 지원)
- 모델: claude-sonnet-4-6 (변경 없음, 프롬프트 변경)
- Vector DB: Pinecone (기존과 동일)

**이번 변경 사항:**
- 시스템 프롬프트 v2.0 → v2.1 업데이트 (응답 형식 변경, 한국어 강화)
- 문서 컬렉션 업데이트 (환불 정책 개정, 신규 제품 추가)
- 청킹 전략 변경 (500토큰 → 300토큰 청크 크기)

**릴리스 제약:**
- 릴리스 목표일: D+7
- 안전성 기준: 100% (단 한 건의 유해 응답도 허용 안 됨)
- 정확도 기준: 90% 이상
- RAG 출처 일치율: 95% 이상

**환경:**
- AI 서비스 엔드포인트: staging.rag-support.internal
- 테스트 사용자 역할: 일반 사용자, 관리자
- 데이터셋 버전: v1.0

## 작업

위 정보를 바탕으로 이번 AI QA 사이클의 전략을 수립하고 `qa-output/ai-qa-strategy.md`를 작성하라.

**판단해야 할 사항:**
1. 변경 유형 분류 (모델 변경 vs 프롬프트 변경 vs RAG 변경)
2. 활성화할 ai-qa 에이전트 및 이유
3. 이번 사이클 품질 게이트 (서비스별 기준)
4. 비교 대상 기준선 (`datasets/results/`의 이전 run 또는 승인된 `datasets/baselines/` 경로)
5. 사용할 데이터셋 버전 및 루브릭

## Acceptance Criteria

- `qa-output/ai-qa-strategy.md` 파일이 존재하고 다음을 포함:
  - 변경 유형 분류 결과 (RAG 변경 + 프롬프트 변경)
  - 활성화 에이전트 목록: ai-evaluator, rag-pipeline-tester, rag-retrieval-tester, ai-perf-observability-tester, ai-safety-tester
  - model-* 테스터 비활성화 이유 명시 (모델 자체는 변경 없음)
  - gen-quality/gen-context 비활성화 이유 명시 (RAG 서비스 — 프롬프트 변경은 rag-retrieval + ai-evaluator A/B로 검증)
  - 품질 게이트: 안전성 100%, 정확도 ≥90%, RAG 출처 일치율 ≥95%
  - 데이터셋 버전: v1.0, suite: rag_release, 루브릭: default + safety
- `qa-output/activation-matrix.json` 파일이 존재하고 `datasets/schemas/activation-matrix.schema.json`을 만족해야 함
  - `run_id: "run-YYYYMMDD-001"` 형식, `suite: "rag_release"` 포함

## 결과 파일 작성

작업 완료 후 `examples/phases/2-ai-qa-cycle/step0-result.json`을 작성하라:
- 성공 → `{"status": "completed", "summary": "AI QA 전략 수립 완료. 변경 유형: RAG+프롬프트. 활성화: ai-evaluator, rag-pipeline-tester, rag-retrieval-tester, ai-perf-observability-tester, ai-safety-tester. gen-*/model-* 비활성화", "artifacts": ["qa-output/ai-qa-strategy.md", "qa-output/activation-matrix.json"]}`
- 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`
