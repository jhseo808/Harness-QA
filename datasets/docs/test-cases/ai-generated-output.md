# AI 생성 산출물 검증 케이스 (AI Generated Output)

AI가 작성한 코드, 테스트케이스, 문서, 설정 파일을 제품 산출물로 사용할 때 검증하는 케이스입니다. 이 영역은 AI 서비스의 응답 품질이 아니라 AI가 만든 산출물의 제품 품질을 다룹니다.

## 케이스 구조

```json
{
  "id": "aigo-{category}-{seq:04d}",
  "version": "1.0.0",
  "dataset_version": "v1.0",
  "category": "code|test_case|documentation|configuration|migration|query",
  "ai_type": "ai_generated_output",
  "suite_tags": ["release", "nightly"],
  "risk_level": "P0|P1|P2|P3",
  "status": "active",
  "input": {
    "task": "AI에게 요청한 원 작업",
    "requirements": [],
    "existing_context": [],
    "generated_output": "검증 대상 산출물"
  },
  "expected": {
    "behavior": "meets_product_quality_bar",
    "evaluation_method": "schema|exact_match|llm_judge|human",
    "pass_threshold": 0.85
  },
  "checks": {
    "requirements_traceability": true,
    "negative_and_boundary_cases": true,
    "security_review": true,
    "maintainability_review": true,
    "execution_or_validation_required": true
  },
  "metadata": {
    "created_at": "ISO8601",
    "source": "human",
    "owner": "ai-qa"
  }
}
```

## 검증 축

| 산출물 | 필수 검증 |
|--------|-----------|
| 코드 | 요구사항 매핑, 예외 처리, 보안 취약점, 기존 아키텍처 적합성, 테스트 가능성, 실제 실행 |
| 테스트케이스 | 요구사항 커버리지, 정상/비정상/경계값, 기대 결과 명확성, 중복, 실행 가능성, 위험 기반 우선순위 |
| 문서 | 사실성, 최신성, 누락, 잘못된 절차, 보안 정보 노출, 사용 대상 적합성 |
| 설정/마이그레이션 | 되돌리기 가능성, 환경별 차이, 비밀값 노출, 호환성, 실패 시 복구 |
| 쿼리 | 권한, 데이터 범위, 성능, 파괴적 변경, 인젝션 취약성 |

## 원칙

- AI 생성 산출물은 초안으로만 간주하고, 제품 반영 전 검증 결과를 남긴다.
- 보안, 데이터 삭제, 권한 변경, 배포 설정을 다루는 산출물은 P0/P1 기준으로 검토한다.
- 테스트케이스를 AI가 만들었을 때도 테스트케이스 자체를 검증 대상에 포함한다.
- 실제 실행이 가능한 산출물은 실행 또는 정적 검증 없이 통과 처리하지 않는다.
