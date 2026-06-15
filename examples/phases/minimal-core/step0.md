# Step 0: setup

## 읽어야 할 파일

- `/docs/` 하위 설계 문서 (PRD, ARCHITECTURE 등)

## 작업

{초기 설정 또는 사전 준비 작업을 기술한다.}

## Acceptance Criteria

{검증 기준을 기술한다. 가능하면 실행 가능한 커맨드로 작성한다.}

## 검증 절차

1. Acceptance Criteria를 확인한다.
2. 작업 완료 후 `phases/minimal-core/step0-result.json`을 작성하라
   (index.json은 수정하지 말 것 — 하네스가 직접 업데이트한다):
   - 성공 → `{"status": "completed", "summary": "한 줄 요약", "artifacts": ["파일 경로"]}`
   - 실패 → `{"status": "error", "error_message": "구체적 에러 내용"}`
   - 개입 필요 → `{"status": "blocked", "blocked_reason": "이유"}`

## 금지사항

- index.json을 직접 수정하지 마라. 이유: 하네스가 자동 관리하는 파일.
