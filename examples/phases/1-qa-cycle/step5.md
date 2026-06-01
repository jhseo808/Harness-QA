# Step 5: reporting (Reporter)

## 컨텍스트

이전 step 산출물을 모두 읽어라:
- `qa-output/qa-strategy.md` — 이번 사이클 품질 게이트
- `qa-output/test-strategy.md` — 테스트 범위, 리스크 분석
- `qa-output/test-cases.md` — 전체 케이스 목록
- `qa-output/coverage-matrix.md` — 커버리지 매트릭스
- `qa-output/api-test-result.md` — API 테스트 결과
- `qa-output/playwright-result.md` — 웹 UI 테스트 결과

## 작업

위 모든 결과를 집계하여 최종 테스트 보고서를 작성하라.
품질 게이트는 `qa-output/qa-strategy.md`에서 가져오고, 없으면 `_base.md`의 기본 게이트를 적용하라.

## Acceptance Criteria

`qa-output/release-report.md`에 다음이 포함:
- Executive Summary (릴리스 권고: 승인 / 조건부 승인 / 차단)
- 전체 케이스 실행 현황 (통과/실패/미실행)
- 발견된 결함 통합 목록 (심각도별 건수)
- 품질 게이트 체크리스트 (통과/실패 여부)
- 미테스트 영역 명시

## 결과 파일 작성

`examples/phases/1-qa-cycle/step5-result.json`:
- 완료 → `{"status": "completed", "summary": "최종 보고서 작성 완료. 릴리스 권고: [승인/조건부/차단]. 총 결함 N건 (P0: N, P1: N).", "artifacts": ["qa-output/release-report.md"]}`
- 산출물 누락으로 진행 불가 → `{"status": "blocked", "blocked_reason": "qa-output/api-test-result.md 파일 없음"}`
