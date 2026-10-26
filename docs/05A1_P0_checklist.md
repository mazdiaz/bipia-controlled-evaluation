# Updated P0 checklist — 05A1

26 October 2026 (Asia/Jakarta). **NO-GO for live inference.** PASS labels apply only to the stated offline scope.

| Gate | Status | Evidence | Remaining gate |
|---|---|---|---|
| P0-A: Source/data integrity | **PASS** | input_hashes.json; data tests | near-duplicate identity remains unknown |
| P0-B: Role/reminder fidelity | **PASS** | source AST/golden prompt tests; token prompt hashes | provider role acceptance unverified under C |
| P0-C: Tokenizer and model access | **BLOCKED** | */token_counts.jsonl; proposed model mapping verified | Token equality PASS in all 880 scenario memberships; account/serialization/context/output adequacy still unverified. |
| P0-D: Neutral semantic controls | **BLOCKED** | arms.json; blank independent reviewer CSVs | two independent semantic approvals and adjudication; final strings not frozen |
| P0-E: Gold/hard-benign validity | **BLOCKED** | blank gold/hard-benign review templates | original gold/answerability and normalization review; no qualified hard-benign set |
| P0-F: Identifiers/error paths | **PASS** | runner tests; */mock_summary.json; history and response ledgers | future live adapter requires separate validation |
| P0-G: Scorer/judge access | **BLOCKED** | scorer_registry.json; synthetic_scores.json; parser/rule tests | judge deployment/access/budget/raw response audit and funded human review not verified; train-only pilot attack-to-rubric mapping absent from test registry |
| P0-H: Sampling/statistics preregistration | **BLOCKED** | candidate case manifests; SIMULATED_analysis.json | final scenario/seed/sample and preregistration not approved; simulation is not power proof |
| P0-I: Permissions/resources | **BLOCKED** | token/call envelopes in summary; BIPIA LICENSE hash | quota/fee cap, reviewer schedule, dataset rights restrictions and judge resources unverified |

Evidence paths in the table are relative to the new local `artifacts-05A1/` build. Shareable counts, summaries and indexes are in `evidence/05A1/`.

Subchecks: exact offline tokens **PASS**; unchanged BIPIA/source/context identity **PASS**; deterministic case/plan regeneration **PASS**; complete suite **PASS (70 tests)**; semantic/gold/hard-benign approvals **BLOCKED**; model/judge access and budget **BLOCKED**; pilot authorization **BLOCKED**. No current gate is failed after remediation, but blocked mandatory gates prevent inference. Historical token failures remain FAIL in the original evidence.

No human decisions were filled. No target/judge/API access call was made. Public documentation inspection does not count as account verification.
