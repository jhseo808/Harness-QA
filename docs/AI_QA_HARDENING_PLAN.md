# AI QA Hardening Plan

## Objective Assessment

Current state: **smoke-operational foundation**.

The AI QA structure has a strong role model, clear AI service taxonomy, dataset manifest, schemas, rubrics, initial adversarial samples, and an executable smoke suite. However, it is not yet a production-grade hard release gate because release, red_team, model_change, RAG, agentic, and nightly suites are still underfilled and the runner does not yet call real model endpoints.

## What Is Strong

- Clear separation between general QA and AI-specific QA.
- Good AI service taxonomy: generative, RAG, agentic, model-change, AI-generated output.
- Sensible agent activation model instead of running every agent every time.
- Manifest-driven suite design with smoke, release, RAG, agentic, model_change, red_team, and nightly suites.
- Append-only results and explicit baseline promotion rules.
- Recent adversarial prompt samples are stored as structured JSON and kept in `pending_review`.
- Smoke suite is executable with active cases.
- Project-level and AI-QA-level audit scripts produce machine-readable and Markdown reports.

## Critical Gaps

### 1. Dataset Is Not Release-Gate Ready

The manifest declares realistic suite sizes. The smoke suite now has enough active cases, but broader suites are still missing active inventory.

Impact:
- `smoke` can be used for controlled pilot checks.
- `release`, `red_team`, and `model_change` cannot be used as hard gates yet.

Required upgrade:
- Promote reviewed cases to `active`.
- Backfill collection inventory to at least smoke level first.
- Keep P0/P1 adversarial samples under human review before activation.

### 2. Runner Is Mock-Ready, Not Endpoint-Ready

There is a runner that can:
- select cases from `datasets/manifest.yaml`,
- write per-case results,
- validate result schema,
- produce suite summaries in mock or dry-run mode.

There is not yet a runner that can:
- call a real model endpoint,
- capture real output, latency, token usage, and cost,
- evaluate real outputs via deterministic checks or LLM-as-Judge,
- write per-case results into `datasets/results/{model_id}/{dataset_version}/{run_id}/cases/`.

Impact:
- The system can rehearse QA execution, but mock results must not be used as release evidence.

Required upgrade:
- Add endpoint adapter support to the AI QA runner.
- Record model config, prompt version, dataset version, and evaluation details per case.

### 3. Judge Calibration Is Missing

The current evaluator correctly says LLM-as-Judge needs calibration, but there is no calibration dataset.

Impact:
- Judge scores cannot be trusted for release decisions.
- Borderline quality and hallucination cases are vulnerable to evaluator bias.

Required upgrade:
- Create at least 30 human-labeled calibration items.
- Track human/judge agreement.
- Block release decisions when alignment is below threshold.

### 4. Agent Count Is High But Not Yet Governed By Evidence

The number of AI QA agents is defensible because the failure modes are genuinely different. The weakness is not the count itself; it is the lack of measurable activation evidence.

Impact:
- Teams may over-run expensive agents.
- Execution plans can become inconsistent between cycles.

Required upgrade:
- Require an `activation_matrix` artifact for every AI QA run.
- Audit skipped agents with explicit rationale.
- Fail the strategy step when model/service type implies a required agent but it is skipped.

### 5. Observability And Feedback Loop Are Not Connected

The structure mentions production feedback and observability, but no import format or promotion workflow is executable.

Impact:
- Real incidents do not automatically become regression coverage.
- Repeated user failures may remain outside the suite.

Required upgrade:
- Define a production feedback ingestion format.
- Route incidents to `datasets/test-cases/feedback/` as `pending_review`.
- Promote recurring reviewed failures into release or nightly suites.

## Hardening Sequence

### Phase 1: Make The Structure Auditable

Done:
- Added `scripts/ai_qa_audit.py`.
- Added `scripts/project_audit.py`.
- Added generated audit outputs:
  - `qa-output/ai-qa-structure-audit.json`
  - `qa-output/ai-qa-structure-audit.md`
  - `qa-output/project-audit.json`
  - `qa-output/project-audit.md`

Next:
- Run the audits in CI or before every QA cycle.
- Treat blocked non-smoke suites as expected until dataset inventory is backfilled.

### Phase 2: Make Smoke Executable

Target:
- `smoke` suite can run end to end.

Minimum inventory:
- capability: 15 active cases
- safety: 10 active cases
- injection_direct: 5 active cases

Acceptance:
- Done: `python scripts/ai_qa_audit.py` reports `smoke` as `ready`.
- Done: `python scripts/ai_qa_runner.py --suite smoke --mode mock ...` writes result files.

### Phase 3: Make Red Team Executable

Target:
- `red_team` suite can run before model or prompt-risk releases.

Minimum inventory:
- safety: 30 active cases
- injection_direct: 20 active cases
- injection_indirect: 20 active cases
- injection_jailbreak: 20 active cases
- injection_agent_specific: 10 active cases

Acceptance:
- P0/P1 prompt injection and jailbreak coverage is active.
- Human-reviewed adversarial prompts are versioned and traceable.

### Phase 4: Add Runner And Evaluation Engine

Required runner modes:
- `--dry-run`: no model call; verifies selection and result paths.
- `--mock`: uses fixture outputs for deterministic CI.
- `--endpoint`: calls a real model endpoint.

Required evaluators:
- exact match
- keyword include/exclude
- JSON schema
- range check
- LLM-as-Judge
- human review placeholder

Acceptance:
- Per-case result files validate against `datasets/schemas/result.schema.json`.
- Summary result includes pass rate, P0/P1 count, cost, latency, and skipped/pending counts.

### Phase 5: Add Calibration And Promotion Governance

Required assets:
- human-labeled judge calibration cases
- feedback ingestion format
- promotion checklist from `pending_review` to `reviewed` to `active`
- baseline promotion checklist

Acceptance:
- LLM-as-Judge is only trusted when human alignment threshold is met.
- Production incidents can become regression cases through a controlled review path.

## Final Target State

The AI QA system should be able to answer these questions automatically:

- Which suite is appropriate for this AI change?
- Which agents must run, and why?
- Are there enough active cases to make the suite meaningful?
- Did the model pass safety, hallucination, format, latency, and cost gates?
- Which failures are model, prompt, context, retrieval, tool, permission, observability, or evaluation problems?
- Can this run be reproduced later?
- Can this result be promoted to a baseline?

Until those questions are answered by artifacts rather than judgment alone, the structure is promising but not yet production-grade.
