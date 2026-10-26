# Chat 5B updated handoff — NO-GO; STOP BEFORE INFERENCE

26 October 2026 (Asia/Jakarta). Read `05A1_remediation_report.md`,
`docs/05A1_amendment_log.md`, `docs/04_experiment_design.md` and
`evidence/05A1/summary.json`. Original reports/evidence remain historical.
This task grants **no live pilot or API access-test authorization**.

Offline revision_4 resolves token equality: 240/240 S180, 600/600 S540 and 40/40
train-only pilot cases have zero N-L/R and N-F/R full-user token deltas using
tiktoken 0.14.0/o200k_base. B0 is intentionally unmatched. Original BIPIA reminder
and all source/case bytes are unchanged. Exact strings/hashes are in
`evidence/05A1/arms.json`; two neutral arms share all sentence words and differ in
punctuation. These controls are **pending human approval**, not preregistered or
certified semantically inert. The complete suite passed 70 tests; see
`evidence/05A1/full_pytest_final.txt`. No target/judge calls occurred.

## Ordered remaining gates

1. Accept or reject the proposed wording amendment with a dated supervisor
   decision. Obtain two independent semantic reviews of all four strings, alone
   and embedded, using `docs/review_05A1/semantic_neutrality.md` and the two blank
   forms. Raters must not have crafted the controls. Any revision restarts review
   and all-case token checks; rejection cannot be overridden by technical PASS.
2. Review all selected source gold: Email answerability/literal unknown,
   Table normalization/multivalue semantics, and symmetric invalidity handling.
   Packets/forms cover the union of scenario alternatives plus pilot: 32 Email
   and 50 Table base records. Original full source/question/gold booklets are
   restricted locally in `artifacts-05A1/review_packets/`. No judgments exist.
3. Construct and double-review eligible hard-benign cases with unchanged answers,
   or explicitly approve a smaller/zero scope before freeze. Blank construction
   and review forms are provided. There are zero real constructed/approved rows.
   New rows must pass full-user equality and source/answer hash checks.
4. Follow `docs/05A1_access_and_budget.md` in a separately authorized future stage:
   confirm named target snapshot, exact role/parameter acceptance, provider framing,
   context/output adequacy, quota, pricing and fee cap. Metadata is insufficient
   proof of inference compatibility. Never silently switch aliases/snapshots or
   normalize/truncate original source. No credentials/credits are established.
5. Approve a named judge snapshot and tested configuration; proposal in
   `config/judge_proposal_05A1.json` uses the target snapshot with an explicit
   correlated-error caveat. Choose a separate judge if required before freeze.
   Keep exact original test rubrics, raw responses, compatibility and strict parser
   results; freeze human audit and missingness handling. **Newly explicit pilot
   blocker:** train attack IDs in `pilot_judge_routes_pending.json` lack audited
   test-registry routes. Develop/review train-specific rubrics prospectively;
   do not borrow similarly named test rules. Pilot judge count remains unknown.
6. Complete cost templates using actual approved prices/limits, judge usage bounds,
   retries/reserve, human review and hard-benign scope. Corrected nominal visible
   target inputs: S180 399,704; S540 952,000; pilot 82,860. These exclude framing,
   judge tokens and retries. Choose one main scenario from resource/precision
   considerations without efficacy outcomes. Freeze scenario/seed, full manifest
   hash, strings/rubric hashes, parameters, exclusions, weights and analysis.
7. Complete P0 permissions, rights, reviewer schedule and explicit researcher
   pilot authorization. A separate authorization is required for main collection.

## Integrity and execution

Use `README.md` 05A1 commands and versioned output folders. Keep original
`artifacts/`, `evidence/`, `05_preflight_report.md` and `HANDOFF_05B.md` intact.
Changed prompts must never be resumed through an old immutable mock ledger.
New offline runs are under `artifacts-05A1/` and `evidence/05A1/`. Historical
primary/backup/revision failures and regression RED logs remain available.

Case manifest SHA-256 values remain:

- S180: `fc1f069c22db82f77986bf797caaf0a4241c851edb3ddfe39891cafecd624f46`
- S540: `b45410c5c8d4de010289bffd59ccf4c067b02cb109158eebeff136432dfa100f`
- Train pilot: `53f2bb5081f4fbcfb8e52e70b5461dd8cfa5fbfe6165336c00c379bf9a21aac5`

Train pilot stays 36 attacked + 4 clean, 160 calls, no test-shared sources or train
Language Translation family. It is an engineering candidate, not approved data.
Both main manifests remain alternatives, neither designated final.

Retain the original handoff's engineering stop rules: any token/role/source/hash
failure, missing/misjoined records or avoidable truncation stops execution. Inspect
differential missingness; provisional limits are ≤2% target missingness and ≤5%
invalid judges, with ≥85% raw rater agreement plus kappa/disagreement review. These
thresholds still require approved operational definitions. No ASR direction is an
acceptance criterion. Preserve failure/charged-timeout uncertainty and all attempts.

Report only engineering feasibility after a future explicitly authorized pilot.
An offline technical PASS does not authorize live inference.
