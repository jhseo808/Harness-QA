# 아키텍처

## 디렉토리 구조
```
{프로젝트 루트}/
├── {진입점 디렉토리}/     # 예: app/, src/, lib/
├── {모듈 디렉토리 1}/     # 예: components/, routes/, handlers/
├── {모듈 디렉토리 2}/     # 예: types/, models/, schemas/
├── {유틸리티}/            # 예: lib/, utils/, helpers/
└── {외부 연동}/           # 예: services/, clients/, adapters/
```

## 패턴
{사용하는 핵심 설계 패턴을 기술한다.
예: "Server Components 기본, 인터랙션이 필요한 곳만 Client Component"
예: "Repository 패턴으로 DB 접근 추상화, Service 레이어에서 비즈니스 로직 처리"}

## 데이터 흐름
```
{데이터가 어떻게 흐르는지 단계별로 기술한다.
예 (웹): 사용자 입력 → UI 컴포넌트 → API 라우트 → 서비스 → DB → 응답 → UI 업데이트
예 (CLI): 커맨드 입력 → 파서 → 핸들러 → 비즈니스 로직 → 저장소 → 출력}
```

## 상태 관리
{상태를 어디서 어떻게 관리하는지 기술한다.
예: "서버 상태는 Server Components, 클라이언트 인터랙션은 useState/useReducer"
예: "전역 상태 없음. 각 핸들러가 독립적으로 처리"}