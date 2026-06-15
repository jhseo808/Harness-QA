# Step 2: verify

## 읽어야 할 파일

- `/docs/` 하위 설계 문서
- 이전 step 산출물 (phases/minimal-core/step0-result.json, step1-result.json 참고)

## 작업

{검증 작업을 기술한다. 테스트 실행, 통합 확인 등.}

## Acceptance Criteria

{검증 기준을 기술한다.}

## 검증 절차

1. Acceptance Criteria를 확인한다.
2. 작업 완료 후 `phases/minimal-core/step2-result.json`을 작성하라:
   - 성공 → `{"status": "completed", "summary": "한 줄 요약", "artifacts": ["파일 경로"]}`
   - 실패 → `{"status": "error", "error_message": "구체적 에러 내용"}`
   - 개입 필요 → `{"status": "blocked", "blocked_reason": "이유"}`

## 금지사항

- index.json을 직접 수정하지 마라.
