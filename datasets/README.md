# datasets/

AI 서비스 평가를 위한 테스트 데이터 저장소입니다.

## 디렉터리 구조

| 디렉터리 | 역할 | 가이드 |
|---------|------|--------|
| `test-cases/` | 실행 가능한 테스트 케이스 JSON | 각 하위 폴더의 README.md |
| `golden/` | 회귀 기준 큐레이션 케이스 | [docs/golden.md](docs/golden.md) |
| `baselines/` | 모델 버전별 집계 지표 | [docs/baselines.md](docs/baselines.md) |
| `rubrics/` | LLM-as-Judge 평가 루브릭 YAML | [docs/results.md](docs/results.md) |
| `schemas/` | JSON Schema 정의 4종 | — |
| `manifest.yaml` | 테스트 suite 구성 및 실행 정책 | — |
| `docs/` | 각 디렉터리 케이스 구조 및 작성 가이드 | — |

## test-cases/ 하위 카테고리

| 경로 | 설명 | 가이드 |
|------|------|--------|
| `injection/` | Prompt injection (direct/indirect/jailbreak/agent-specific) | [docs/test-cases/injection/](docs/test-cases/injection/) |
| `hallucination/` | 환각 (factual/rag-grounding/reference/self-knowledge) | [docs/test-cases/hallucination/](docs/test-cases/hallucination/) |
| `capability/` | 기능 품질 (qa/summarization/translation/classification 등) | [docs/test-cases/capability.md](docs/test-cases/capability.md) |
| `safety/` | 안전 (violence/self-harm/illegal/hate/PII 등) | [docs/test-cases/safety.md](docs/test-cases/safety.md) |
| `feedback/` | 사용자 피드백 기반 회귀 케이스 | [docs/test-cases/feedback.md](docs/test-cases/feedback.md) |
| `ab/` | A/B 비교 케이스 | [docs/test-cases/ab.md](docs/test-cases/ab.md) |
| `ai-generated-output/` | AI 산출물(코드/문서/설정) 품질 검증 | [docs/test-cases/ai-generated-output.md](docs/test-cases/ai-generated-output.md) |

## 처음 사용한다면

1. `manifest.yaml`로 suite 구성 파악
2. 해당 카테고리 `docs/` 가이드로 케이스 구조 확인
3. 기존 케이스(예: `test-cases/injection/direct/`)를 참고해 새 케이스 작성
4. 실행 결과는 `datasets/results/{model_id}/{dataset_version}/{run_id}/`에 저장됨 (gitignore)
