<!--
  [템플릿 안내] 이 파일은 하네스가 모든 Claude 프롬프트에 자동 주입하는 프로젝트 컨텍스트입니다.
  {중괄호} 항목을 실제 프로젝트 기술 스택과 규칙으로 교체한 뒤 이 주석을 삭제하세요.
  작성 예시: docs/CLAUDE_SETUP_GUIDE.md 참고
-->

# 프로젝트: {프로젝트명}

## 기술 스택
- {프레임워크 (예: Next.js 15)}
- {언어 (예: TypeScript strict mode)}
- {스타일링 (예: Tailwind CSS)}

## 아키텍처 규칙
- CRITICAL: {절대 지켜야 할 규칙 1 (예: 모든 API 로직은 app/api/ 라우트 핸들러에서만 처리)}
- CRITICAL: {절대 지켜야 할 규칙 2 (예: 클라이언트 컴포넌트에서 직접 외부 API를 호출하지 말 것)}
- {일반 규칙 (예: 컴포넌트는 components/ 폴더에, 타입은 types/ 폴더에 분리)}

## 개발 프로세스
- CRITICAL: 새 기능 구현 시 반드시 테스트를 먼저 작성하고, 테스트가 통과하는 구현을 작성할 것 (TDD)
- 커밋 메시지는 conventional commits 형식을 따를 것 (feat:, fix:, docs:, refactor:)

## 명령어
npm run dev      # 개발 서버
npm run build    # 프로덕션 빌드
npm run lint     # ESLint
npm run test     # 테스트

---

## 하네스 구조 평가 (Harness-QA 전용)

이 저장소 자체의 구조는 `assessments/`에서 주기적으로 평가한다.
평가 대상은 하네스 구조(실행 방식, step 계약, agent 구조, 확장 경계, 온보딩 구조)이며, QA 실행 결과나 모델 응답 품질은 평가하지 않는다.

- 최신 평가: `assessments/latest.md`
- 평가 이력: `assessments/history.md`
- 루브릭: `assessments/rubrics/harness-structure-rubric.v1.md`
- 평가 요청 방법: `assessments/README.md`

하네스 구조를 크게 변경한 뒤에는 평가를 새로 실행해 변경 영향을 기록한다.