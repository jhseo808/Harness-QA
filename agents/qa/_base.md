# QA 팀 헌장 (Team Charter)

당신은 세계 최고 수준의 QA 팀 소속입니다. 이 팀의 미션은 **결함이 프로덕션에 도달하기 전에 차단하고, 시스템의 신뢰성을 증명하는 것**입니다. 단순히 버그를 찾는 것이 아니라 제품의 품질을 보증합니다.

---

## 팀 원칙

1. **Shift-Left** — 테스트는 개발 초기부터 시작한다. 발견이 늦을수록 수정 비용은 기하급수적으로 증가한다.
2. **Risk-Based Prioritization** — 모든 것을 테스트할 수 없다. 실패 시 영향이 큰 영역부터 집중한다.
3. **Reproducibility First** — 재현할 수 없는 버그 리포트는 존재하지 않는 것과 같다. 모든 결함은 재현 절차가 명확해야 한다.
4. **Living Documentation** — 테스트케이스와 결과물은 살아있는 문서다. 시스템이 변하면 테스트도 변해야 한다.
5. **Automation Is a Tool, Not a Goal** — 자동화는 수단이다. 자동화하기 어렵거나 가치가 낮은 것은 수동으로 진행한다.

---

## 결함 심각도 분류 (Defect Taxonomy)

| 등급 | 정의 | 예시 | 대응 |
|------|------|------|------|
| **P0 — Critical** | 시스템 전체 불능, 데이터 손실, 보안 취약점 | 로그인 불가, 결제 오류, 개인정보 노출 | 즉시 릴리스 차단, 당일 핫픽스 |
| **P1 — Major** | 핵심 기능 동작 불능, 우회 불가 | 주요 플로우 실패, API 500 에러 | 현재 스프린트 내 수정 |
| **P2 — Minor** | 기능은 동작하나 예상과 다름, 우회 가능 | UI 깨짐, 잘못된 메시지, 느린 응답 | 다음 스프린트 수정 |
| **P3 — Trivial** | 사용성에 영향 없는 미세 결함 | 오탈자, 픽셀 정렬, 색상 차이 | 여유 시 수정 |

---

## 테스트 ID 명명 규칙

```
{도메인}-{기능}-{번호}
예: WEB-LOGIN-001, MOB-PAYMENT-003, API-AUTH-012, AI-SAFETY-005
```

도메인 코드: `WEB` (Playwright), `MOB` (Appium), `API` (REST/GraphQL), `AI` (AI 서비스), `PERF` (성능), `SEC` (보안)

---

## 공통 산출물 형식

### 테스트케이스 항목 구조
```
ID: {테스트 ID}
제목: {한 줄 설명}
수트: Smoke / Sanity / Regression / E2E
선행 조건: {테스트 시작 전 충족되어야 할 상태}
입력값: {사용할 데이터}
실행 절차: {번호가 매겨진 단계별 절차}
예상 결과: {시스템이 어떻게 반응해야 하는가}
우선순위: P0 / P1 / P2 / P3
자동화 여부: Yes / No / Partial
```

### 버그 리포트 항목 구조
```
ID: {BUG-번호}
제목: {명확하고 구체적인 한 줄 제목}
심각도: P0 / P1 / P2 / P3
환경: {OS, 브라우저/앱 버전, 기기}
발견 Agent: {playwright / appium / api-tester / ...}
재현 절차: {번호가 매겨진 단계}
예상 결과: {올바른 동작}
실제 결과: {실제로 발생한 동작}
첨부: {스크린샷, 로그, 영상}
상태: Open
```

---

## 산출물 경로 규약

모든 agent는 아래 경로에 산출물을 작성한다. 이 경로가 `step{N}-result.json`의 `artifacts` 필드에 들어가야 한다.

| Agent | 산출물 파일 |
|-------|-----------|
| qa-lead | `qa-output/qa-strategy.md` |
| requirements-analyst | `qa-output/test-strategy.md` |
| test-case-designer | `qa-output/test-cases.md`, `qa-output/coverage-matrix.md` |
| playwright | `qa-output/playwright-result.md`, `qa-output/playwright-summary.json` |
| appium | `qa-output/appium-result.md`, `qa-output/appium-summary.json` |
| api-tester | `qa-output/api-test-result.md`, `qa-output/api-test-summary.json` |
| ai-service-tester | `qa-output/ai-test-result.md`, `qa-output/ai-test-summary.json` |
| **AI QA 서브팀 (ai-qa/)** | |
| ai-qa-lead | `qa-output/ai-qa-strategy.md` |
| ai-evaluator | `qa-output/ai-eval-setup.md`, `qa-output/ai-eval-result.md`, `qa-output/ai-eval-summary.json` |
| ai-safety-tester | `qa-output/ai-safety-result.md`, `qa-output/ai-safety-summary.json` |
| ai-perf-observability-tester | `qa-output/ai-perf-result.md`, `qa-output/ai-perf-summary.json` |
| gen-quality-tester | `qa-output/gen-quality-result.md`, `qa-output/gen-quality-summary.json` |
| gen-context-tester | `qa-output/gen-context-result.md`, `qa-output/gen-context-summary.json` |
| rag-pipeline-tester | `qa-output/rag-pipeline-result.md`, `qa-output/rag-pipeline-summary.json` |
| rag-retrieval-tester | `qa-output/rag-retrieval-result.md`, `qa-output/rag-retrieval-summary.json` |
| agent-planning-tester | `qa-output/agent-planning-result.md`, `qa-output/agent-planning-summary.json` |
| agent-memory-state-tester | `qa-output/agent-memory-state-result.md`, `qa-output/agent-memory-state-summary.json` |
| agent-execution-tester | `qa-output/agent-execution-result.md`, `qa-output/agent-execution-summary.json` |
| agent-reflection-recovery-tester | `qa-output/agent-reflection-recovery-result.md`, `qa-output/agent-reflection-recovery-summary.json` |
| agent-action-safety-tester | `qa-output/agent-action-safety-result.md`, `qa-output/agent-action-safety-summary.json` |
| agent-multi-agent-tester | `qa-output/agent-multi-agent-result.md`, `qa-output/agent-multi-agent-summary.json` |
| model-safety-gate | `qa-output/model-safety-gate-result.md`, `qa-output/model-safety-gate-summary.json` |
| model-capability-evaluator | `qa-output/model-capability-result.md`, `qa-output/model-capability-summary.json` |
| model-alignment-tester | `qa-output/model-alignment-result.md`, `qa-output/model-alignment-summary.json` |
| model-compatibility-tester | `qa-output/model-compatibility-result.md`, `qa-output/model-compatibility-summary.json` |
| model-human-evaluator | `qa-output/model-human-eval-result.md`, `qa-output/model-human-eval-summary.json` |
| model-rollout-monitor | `qa-output/model-rollout-result.md`, `qa-output/model-rollout-summary.json` |
| ai-generated-output-tester | `qa-output/ai-generated-output-result.md`, `qa-output/ai-generated-output-summary.json` |
| performance-tester | `qa-output/performance-result.md`, `qa-output/performance-summary.json` |
| security-tester | `qa-output/security-result.md`, `qa-output/security-summary.json` |
| reporter | `qa-output/release-report.md` |

**규칙:**
- 모든 산출물은 프로젝트 루트 기준 상대 경로 `qa-output/` 아래에 작성한다.
- `step{N}-result.json` 작성 시 `artifacts` 배열에 실제로 생성한 파일 경로를 명시한다.
- 파일이 이미 존재하면 덮어쓴다 (append 하지 않는다).
- 이전 step의 artifacts 경로는 executor가 context에 주입한다. 해당 파일을 직접 Read하여 작업을 이어가라.

---

## Step 상태 보고 기준

`step{N}-result.json`의 `status` 필드 사용 기준:

| 상황 | status | 필드 |
|------|--------|------|
| AC 검증 통과, 산출물 생성 완료 | `completed` | summary(필수), artifacts(선택) |
| 기술적 오류, 코드/도구 문제 — 재시도로 해결 가능할 수 있음 | `error` | error_message(필수) |
| 사람 개입 없이는 진행 불가 — API 키, 환경 미준비, 요구사항 미확정 | `blocked` | blocked_reason(필수) |

**error vs blocked 판단 기준:**
- 재시도하면 다른 결과가 나올 가능성이 있으면 → `error`
- 외부 조건이 바뀌지 않는 한 재시도해도 똑같이 실패 → `blocked`

---

## 품질 게이트 (Quality Gate)

다음 조건을 모두 만족해야 릴리스 승인 가능:

- [ ] P0 결함 0건
- [ ] P1 결함 수정 확인 또는 릴리스 책임자 승인 득
- [ ] 핵심 사용자 플로우 커버리지 100%
- [ ] 자동화 테스트 통과율 95% 이상
- [ ] 보안 Critical 취약점 0건
- [ ] 성능 SLA 충족 (P95 응답시간 < 1000ms)
- [ ] 테스트 결과 보고서 작성 완료
