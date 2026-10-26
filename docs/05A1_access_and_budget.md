# Access and budget preparation — no calls authorized

Prepared 26 October 2026 (Asia/Jakarta). No target-model API, model metadata API,
or judge API was called. No credential was requested/read and no balance or credit
was inferred. Public documentation was read only to prepare these instructions.

## Future researcher access verification

The target remains `gpt-5.4-mini-2026-03-17`. It is listed in the
[official model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini).
A public listing does not establish project access or compatible serialization.

1. In the intended organization/project, have the researcher inspect model
   permissions, billing authorization, RPM/TPM, project spend controls and available
   resources. Record dated, redacted evidence and project identity in
   `docs/review_05A1/forms/access_budget_approval.csv`. Never save secret keys.
   Limits are organization/project/model dependent; use the
   [official limits guidance](https://developers.openai.com/api/docs/guides/rate-limits).
2. In a **separately authorized future metadata-access stage**, an authorized
   researcher can issue `GET /v1/models/gpt-5.4-mini-2026-03-17` with their own
   credentials. The [retrieve-model reference](https://developers.openai.com/api/reference/resources/models/methods/retrieve)
   describes this metadata endpoint. Preserve redacted status/body and request ID.
   This instruction is not a command executed by this remediation. A successful
   metadata lookup does not prove generation, parameter or role support. A failure
   leaves access blocked; do not use an alias or silently choose a replacement.
3. Before any generation, reconcile current endpoint documentation and account
   settings with the exact two-role request: generic BIPIA system message followed
   by the combined user message, cap 512, proposed temperature 0,
   reasoning_effort none, no tools. Settings are proposals even when publicly
   described. Do not assume simultaneous parameter compatibility. An unsupported
   field needs a documented, uniformly applied protocol decision, then new hashes.
4. Actual generation compatibility, usage/framing, finish reasons, output adequacy
   and provider transformations require a **separately authorized, budgeted benign
   engineering request**. It is inference and must not be disguised as a free
   connectivity test. Preserve exact serialized messages/parameters and returned
   model/usage. Do not send held-out test examples to validate access. First resolve
   approvals; this task authorizes no such request.
5. Record empirical context acceptance against the maximum visible input per call
   in the envelope CSV plus framing and output cap. Never truncate source/question
   or shorten guidance to fit. If the snapshot is unavailable, stop and obtain an
   approved named replacement with faithful tokenizer and fresh offline validation.

## Proposed judge configuration and approvals

`config/judge_proposal_05A1.json` proposes the same named snapshot for an economical
feasibility configuration, **not an approved judge or a claim of independence**.
Using the target model as judge creates correlated-error concerns. The supervisor
must approve that tradeoff or select a distinct named snapshot before freeze.
No choice may be based on which judge makes the reminder look effective.

Use exact original BIPIA test rubrics/suffix, newline replacement and single-user
chat renderer, with cap 32 and candidate temperature 0/reasoning none. Retain raw
responses and both parser results; strict UNKNOWN/invalid/missing remain unresolved.
Keep deterministic scorer routes separate. Freeze retry/error/truncation policy,
human audit and invalid-rate limits. Public existence is not account access.

**Additional blocker discovered:** the audited test registry does not cover the
six selected train-only pilot attack IDs (Anagramming-0/-4, Content Creation-3/-4,
Social Interaction-2/-3). See `evidence/05A1/pilot_judge_routes_pending.json`.
The pilot's 36 attacked records cannot be assigned test rubrics by name guessing.
An explicit train-goal rubric/mapping and independent review are required before
pilot scoring. Pilot model-judge call count remains unknown. This does not affect
the verified held-out test registry or token equality. The materials generator's
initial KeyError is preserved in `materials_execution_failed.txt`; the corrected
generator records unresolved routing rather than inventing a judge count.

## Corrected resource envelopes

`evidence/05A1/target_token_envelopes.csv` contains scenario × task × arm sums,
min/max user counts and maximum visible input per request. These are text tokens
under tiktoken 0.14.0/o200k_base, not billed provider usage.

| Candidate | Target calls | Visible input tokens | Output cap at 512/call | Nominal model-judge calls |
|---|---:|---:|---:|---:|
| S180 | 960 | 399,704 | 491,520 | 624 |
| S540 | 2,400 | 952,000 | 1,228,800 | 1,764 |
| Train pilot | 160 | 82,860 | 81,920 | unresolved |

Rows exclude approved hard-benign records (none), provider framing, judge tokens,
retries and human work. The existing target ledger caps at three total attempts:
the conservative target replay envelope is 2,880 calls / 1,199,112 visible input /
1,474,560 output for S180 and 7,200 / 2,856,000 / 3,686,400 for S540. This is an
attempt envelope, not expected cost or remote exactly-once proof. No target adapter
exists. A future adapter must enforce an approved total cap and retain charged
timeouts/errors. Judge retry resources are separately unresolved.

Use `evidence/05A1/cost_estimation_template.csv`. Blank numeric cells mean
**unknown, never zero**. Prices remain unresolved for approved account, service
tier, currency, region and run date; public catalog prices are not inserted as an
approved budget. Do not assume cache hits, discounts, credits or grants.

For each alternative, define N = attempted target calls, V = total visible target
input across those attempts, F = unknown additional framing tokens, O = charged
target output, JI/JO = charged judge input/output, and PI/PO/JPI/JPO = approved
per-million prices. With no assumed caching:

```text
target_cost = ((V + F) * PI + O * PO) / 1,000,000
judge_cost = (JI * JPI + JO * JPO) / 1,000,000
human_cost = reviewer_hours * reviewer_hourly_cost + adjudication_cost + output_audit_cost
subtotal = target_cost + judge_cost + human_cost + approved_hard_benign_cost
fee_envelope = subtotal * (1 + approved_reserve_fraction) + taxes_and_fx_adjustment
```

Nominal S180/S540 judge counts are all planned attacked arms routed to model
scoring, before target failures, judge retries or audit sampling. Judge input
depends on rubric plus actual target output and cannot be obtained from mocked
responses as if measured. Unknown prices or JI/JO make the total unresolved.
An optional prospective bound may tokenize all fixed rubrics with the chosen judge
tokenizer and conservatively bound target-output expansion, but requires an
approved assumption and is not an observed budget.

Adding h qualified hard-benign cases adds 4h target calls and up to 2048h nominal
output tokens; input must be rendered/recounted from actual approved records.
The earlier ceiling h=24 would add 96 calls/49,152 output tokens, not a planned or
approved count. Keep this increment and pilot costs separate from main-run costs.

Choose S180 or S540 only after price/usage/quota, fee cap, retry reserve, reviewer
capacity and prospective precision rationale are approved. Freeze one manifest;
do not sum alternatives as if both are authorized. Access, semantics, gold,
hard-benign scope, judge routing and pilot authorization remain separate gates.
