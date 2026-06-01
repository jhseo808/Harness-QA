# Step 3: api-testing (API Tester)

## 컨텍스트

이전 step 산출물을 먼저 읽어라:
- `qa-output/test-cases.md` — api-tester에 배정된 케이스 ID 목록
- `qa-output/test-strategy.md` — API 스펙, 비즈니스 규칙

테스트 환경:
- Base URL: `http://localhost:3000`
- 인증: 없음 (MVP)

## 작업

배정된 케이스를 기반으로 API 테스트를 실행하고 결과를 `qa-output/api-test-result.md`에 작성하라.

**반드시 검증할 항목:**
1. 상태 코드 (2xx/4xx 구분)
2. 응답 스키마 (필드명, 타입, null 처리)
3. 입력 유효성 — 빈 title POST, 존재하지 않는 ID PATCH/DELETE
4. HTTP 멱등성 — DELETE 후 재삭제 시 404
5. 빈 배열 응답 — `[]` vs `null` 구분

## Acceptance Criteria

`qa-output/api-test-result.md`에 다음이 포함:
- 케이스별 통과/실패 결과
- 발견된 결함 (BUG-XXX 형식)
- 미검증 항목 및 이유

## 결과 파일 작성

`examples/phases/1-qa-cycle/step3-result.json`:
- 성공 → `{"status": "completed", "summary": "API 테스트 N개 실행. 통과: N, 실패: N. 결함 N건 발견.", "artifacts": ["qa-output/api-test-result.md", "qa-output/api-test-summary.json"]}`
- 환경 문제 (서버 미실행 등) → `{"status": "blocked", "blocked_reason": "http://localhost:3000 접근 불가"}`
- 재시도 가능 실패 → `{"status": "error", "error_message": "구체적 에러 내용"}`
