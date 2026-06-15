# Step 1: implement

## 읽어야 할 파일

- `/docs/` 하위 설계 문서
- 이전 step에서 생성된 파일 (phases/minimal-core/step0-result.json 참고)

## 작업

{구현 작업을 기술한다. 파일 경로, 인터페이스 수준 지시를 포함한다.}

## Acceptance Criteria

{검증 기준을 기술한다.}

## 검증 절차

1. Acceptance Criteria를 확인한다.
2. 작업 완료 후 `phases/minimal-core/step1-result.json`을 작성하라:
   - 성공 → `{"status": "completed", "summary": "한 줄 요약", "artifacts": ["파일 경로"]}`
   - 실패 → `{"status": "error", "error_message": "구체적 에러 내용"}`
   - 개입 필요 → `{"status": "blocked", "blocked_reason": "이유"}`

## 금지사항

- index.json을 직접 수정하지 마라.
- 이 step 범위를 벗어난 추가 파일을 생성하지 마라.
