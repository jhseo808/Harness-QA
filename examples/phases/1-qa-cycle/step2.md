# Step 2: test-case-design (Test Case Designer)

## 컨텍스트

이전 step 산출물을 먼저 읽어라:
- `qa-output/qa-strategy.md` — 활성화된 agent 목록 확인 (케이스 배정 대상)
- `qa-output/test-strategy.md` — AC, 리스크 매트릭스, 통합 접점

## 작업

test-strategy.md를 바탕으로 테스트케이스를 설계하고 두 파일을 작성하라.
활성화된 agent(api-tester, playwright)에게만 케이스를 배정하라.

## Acceptance Criteria

- `qa-output/test-cases.md`: 전체 케이스 목록 (ID, 수트, 우선순위, 선행 조건, 입력값, 예상 결과 포함)
- `qa-output/coverage-matrix.md`: 요구사항 ↔ 케이스 매핑 표, 미커버 항목 명시
- P0 케이스 100% Smoke 수트 배정
- Negative 케이스 비율 ≥ 40%

## 검증 절차

1. Acceptance Criteria를 모두 충족했는지 확인한다.
2. 작업 완료 후 `examples/phases/1-qa-cycle/step2-result.json`을 작성하라:
   - 성공 → `{"status": "completed", "summary": "케이스 N개 설계. Smoke: N, Regression: N, E2E: N. api-tester 배정: N건, playwright 배정: N건.", "artifacts": ["qa-output/test-cases.md", "qa-output/coverage-matrix.md"]}`
   - 진행 불가 → `{"status": "blocked", "blocked_reason": "이유"}`

## 금지사항

- 테스트를 실행하지 마라. 이유: 실행은 step 3(api-tester), step 4(playwright)에서 담당.
- qa-strategy.md에서 활성화되지 않은 agent(예: performance-tester)에 케이스를 배정하지 마라. 이유: 확정된 범위 이탈.
