# Chat 5B handoff — STOP BEFORE LIVE INFERENCE

Offline implementation is available and tested. **No live pilot is authorized by
this task. NO-GO** until the protocol's mandatory gates are met and the researcher
explicitly authorizes the future pilot. Do not interpret a successful mock run as
defense efficacy, model access, or approval of control semantics.

## Starting artifacts

- Read `05_preflight_report.md`, `docs/04_experiment_design.md` and
  `evidence/verified_summary.json`.
- Reproduce using `README.md` and `requirements-lock.txt`; verify source commit and
  `evidence/input_hashes.json` before making any changes.
- Both candidate manifests use seed 20261026, 30 unique source groups/task, one
  base question/source; all 15 held-out families and 3 positions. S180 = 180 attacked
  + 60 clean cases; S540 = 540 + 60. Neither is final. No approved hard-benign rows.
- Local full cases/plans and blank reviewer forms are in `artifacts/`.
  `pilot_CANDIDATE_cases.jsonl` has **36 attacked + 4 clean train-only cases**
  (160 four-arm invocations), no test-shared source groups, no train Language
  Translation family. This is a candidate engineering pilot list, not permission
  to run it. These pilot cases have not received gold/hard-benign review.

## Required next work, before any target/judge call

1. Resolve token failure: primary N-F is **+5**, N-L **+5/+6** full-user tokens
   versus R. Preserve the current measured failures and string hashes. Evaluate
   predeclared backups offline if appropriate, with dated rationale and fresh full
   case counts; otherwise formally amend the protocol. Do not change the reminder,
   pad with meaningless characters, permit per-case wording, or optimize on outputs.
   This run made **no neutral-text revision** and evaluated candidate 1 only.
2. Obtain two independent semantic reviews for every final task/control string,
   including embedded templates; adjudicate and freeze approved strings/hashes.
3. Double-review selected original gold and Email unknown answerability; approve
   normalization rules. Establish and double-approve the hard-benign set or
   explicitly shrink it before freeze. Retain rejected/ambiguous IDs and reasons.
4. In a separately authorized access-validation stage, establish the named target
   snapshot and faithful tokenizer, allowed request parameters, exact two-role
   content acceptance, context capacity, quota and budget. **Do not assume**
   temperature=0/reasoning_effort=none/output settings are supported. Do not silently
   switch model if unavailable; obtain protocol approval for a named replacement.
5. Select/pin a judge deployment and resources. Verify exact rubric formatting,
   raw judge-response retention, missingness handling, original-compatible and strict
   parsing, and planned human output audit. The offline renderer is available;
   no judge adapter/account was tested. All 75 scorer routes have been audited.
6. Choose S180/S540 from token/call budget, reviewer capacity and prospective
   sensitivity/precision reasoning. No budget is approved. Freeze seed, final
   manifest hash, alpha, exclusions, weights, bootstrap and missingness analysis
   before test inference. Synthetic CIs are not empirical effect or power evidence.
7. Verify dataset rights and restricted raw-file handling, reviewer schedule,
   fee cap and reserve. Record all P0 evidence and explicit researcher authorization.

## Future pilot stop rules

After authorization, use train-only pilot IDs, never test efficacy to revise controls.
Halt if any P0 gate fails, tokens mismatch, role/source/hash integrity fails, a record
is shifted/duplicated/absent, or avoidable truncation occurs. Inspect differential
missingness and clustering; protocol provisional engineering limits are ≤2% final
target missingness and ≤5% invalid judges. Review ≥85% raw rater agreement plus
kappa/disagreement types. Fix infrastructure/rubrics with a dated amendment, preserve
the failed evidence, rerun engineering checks, and obtain renewed approval as needed.
No ASR direction is a pilot acceptance criterion.

For a future provider adapter, preserve invocation ID/case/arm/replicate and prompt
hash through dispatch and completion. Persist all planned rows first; retain attempts,
timestamps, finish reason, token usage and transport errors. Never zip a shortened
response list to metadata. A timeout may have unknown provider-side completion:
record uncertainty and any cost, and do not claim exactly-once remote execution.
Current SQLite ledgers require one coordinator each and intentionally keep terminal
failures; use versioned runs rather than deleting inconvenient failures.

Report only engineering feasibility after the future authorized pilot. Main held-out
collection requires its own freeze and authorization.
