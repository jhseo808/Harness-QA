# AI QA Dataset Documentation

This directory contains human-facing documentation for dataset management.

Dataset folders under `datasets/test-cases/`, `datasets/results/`, `datasets/baselines/`, and `datasets/golden/` should contain data artifacts only. Category guides live here so data directories stay clean and machine-oriented.

## Core Documents

- `baselines.md` — approved baseline summary format and promotion rules
- `golden.md` — golden dataset structure and governance
- `results.md` — append-only run result storage rules

## Test Case Guides

- `test-cases/capability.md`
- `test-cases/safety.md`
- `test-cases/ab.md`
- `test-cases/feedback.md`
- `test-cases/ai-generated-output.md`

## Hallucination Guides

- `test-cases/hallucination/factual.md`
- `test-cases/hallucination/reference.md`
- `test-cases/hallucination/rag-grounding.md`
- `test-cases/hallucination/self-knowledge.md`

## Injection Guides

- `test-cases/injection/direct.md`
- `test-cases/injection/indirect.md`
- `test-cases/injection/jailbreak.md`
- `test-cases/injection/agent-specific.md`
