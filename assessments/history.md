# 하네스 구조 평가 이력

이 파일은 run 기반 하네스 구조 평가 이력을 추적한다.
기존 `v1.x.md` 평가는 `assessments/legacy/` 아래에 역사적 맥락으로 유지한다.

| 평가 ID | 날짜 | 루브릭 | 평가자 | 비교 대상 | 점수 | 등급 | 주요 리스크 | 주요 변경 영향 | 주요 개선 |
|---|---|---|---|---|---:|---|---|---|---|
| assess-20260614-001 | 2026-06-14 | harness-structure-rubric.v1 | Codex / GPT-5 | none | 89 | 구조는 있으나 무거움 | QA/AI-QA 경계 혼입, qa-output 커밋 정책 불일치, activation matrix 수동 변환 의존 | 첫 run. dirty working tree 기준으로 기준점 생성 | base 계약 분리, 커밋 정책 정합화, activation matrix 변환 계약 표준화 |
| assess-20260614-002 | 2026-06-14 | harness-structure-rubric.v1 | Codex / GPT-5 | assess-20260614-001 | 95 | 매우 우수한 구조 | activation guide의 reporter 경로 불일치, runner adapter 문서화 부족, activation matrix 수동 변환 의존 | 001 개선안 대부분 반영. QA/AI-QA base 분리, qa-output 정책 정합화, runner 호출부 분리, minimal-core 추가 | reporter 경로 정합화, minimal-core 온보딩 전면화, runner adapter 교체 지점 문서화 |
