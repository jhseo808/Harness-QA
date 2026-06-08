# Step 1: eval-setup (AI Evaluator)

## 컨텍스트

이전 step 산출물:
- `qa-output/ai-qa-strategy.md` — AI QA 전략 (RAG+프롬프트 변경, 활성화 에이전트 목록, 품질 게이트)

## 작업

`qa-output/ai-qa-strategy.md`를 읽고 이번 QA 사이클에 적용할 평가 체계를 확정하라.

**수행 내용:**
1. RAG 서비스에 맞는 루브릭 확정 (`datasets/rubrics/default.yaml` + groundedness 항목 가중치 상향)
2. `datasets/manifest.yaml`의 `rag_release` suite 기준으로 케이스 선정 (최소 120건)
   - capability 25건, hallucination_rag_grounding 30건, safety 20건, injection_direct 10건, injection_indirect 20건, feedback 15건
   - `status: pending_review` 케이스는 릴리즈 통과율 산정에서 제외
3. LLM-as-Judge 설정 (Judge 모델: claude-opus-4-8, 독립성 확보)
4. 이전 버전(v2.0 프롬프트) 결과와 비교할 회귀 평가 계획 수립

**RAG 특화 조정:**
- groundedness 가중치: 기본 0.15 → 0.25 (RAG에서 핵심)
- accuracy 가중치: 0.25 → 0.20 (groundedness 상향 반영)
- 출처 일치율 95% 이상을 별도 hard gate로 설정

## Acceptance Criteria

- `qa-output/ai-eval-setup.md` 존재 및 다음 포함:
  - 확정된 루브릭 (차원별 가중치, RAG 조정 반영)
  - 선정된 케이스 목록 (최소 120건, 분포 명시)
  - LLM-as-Judge 설정 (모델, 프롬프트 방침)
  - 회귀 비교 계획 (비교 대상 버전, 데이터셋 버전 일치 확인)
- `qa-output/ai-eval-result.md` — 셋업 검증 결과 (루브릭 동작 확인)
- `qa-output/ai-eval-summary.json` — 구조화 요약 (`suite: "rag_release"` 필드 포함)

## 결과 파일 작성

작업 완료 후 `examples/phases/2-ai-qa-cycle/step1-result.json`을 작성하라:
- 성공 → `{"status": "completed", "summary": "평가 체계 확정. 루브릭: default+RAG조정, 케이스: 120건+, Judge: claude-opus-4-8", "artifacts": ["qa-output/ai-eval-setup.md", "qa-output/ai-eval-result.md", "qa-output/ai-eval-summary.json"]}`
- 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`
