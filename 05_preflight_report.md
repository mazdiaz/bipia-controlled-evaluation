# 05 — Offline implementation and preflight report

Date: 26 October 2026 (Asia/Jakarta). **Recommendation: NO-GO for Chat 5B live pilot.**
No target-model or judge inference occurred; no API credits or credentials were used.
All model responses are MOCK and all statistical outcomes are SIMULATED.

## Verified execution

Implemented a separate Python package, with the official BIPIA archive at
`a004b69ec0dd446e0afd461d98cb5e96e120a5d0`. Python 3.14.0, pinned dependencies in
`requirements-lock.txt`. Final test command:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --junitxml=evidence/pytest.xml
```

**46 passed in 10.85 seconds** (`evidence/final_pytest.txt`, `evidence/pytest.xml`).
The tests deny outbound network connections; loopback is allowed for Windows asyncio.
Artifact command `python -m preflight` also completed, with explicit failed/blocked
research gates. See `evidence/final_preflight.txt` and `evidence/COMMANDS.md`.
Earlier failing tests and corrections remain in numbered evidence logs. They are
superseded by the final suite, not represented as successful runs.

A fresh code reviewer separately ran 18 runner/scoring/analysis tests and found no
important/critical defects. Additional subprocess-crash and exact offline judge-format
tests were added afterward. `evidence/code_review.md` records scope and limitations.

## Source and data integrity

All 23 audited files have recorded canonical SHA-256 and Git blob SHA;
audited working-tree bytes equal pinned blobs. The archive has no source-code edits.
Windows autocrlf initially changed checkout line endings; audited files were restored
from exact pinned blobs and the local index refreshed. The loader reads Git blobs,
never normalized source strings. Acquisition instructions disable autocrlf initially.

| Task | Train/test rows | Distinct train/test sources | Exact shared sources | Test literal unknown |
|---|---:|---:|---:|---:|
| email | 50/50 | 45/44 | 11 | 26 |
| table | 900/100 | 617/84 | 0 | 0 |

Schema is exactly three string fields: context, question, ideal. All 11 shared Email
groups (11 train rows) are excluded from development; held-out test sources remain.
Each attack split has 15 families × 5 variants. Language Translation is the sole
shared family name, with no exact shared payload; it is excluded from strict
family-disjoint development. Near-duplicate identity is not established.

Exact WOSystem user templates, generic system string and unchanged reminder pass
AST/golden comparisons against pinned source. All four arms have system/user roles
and differ only in guidance. Insertion tests match original start/end/seeded Punkt
sentence-start middle behavior. Context/question/payload hashes and actual character
and UTF-8 byte insertion boundaries are retained. Middle is not geometric midpoint.

## Candidate samples and resource envelope

Engineering seed 20261026; neither scenario nor seed is approved for main research.
Each selects one question from 30 distinct sources/task (60 clusters). Email has
15 literal unknown and 15 answerable-label candidates; Table has 15 numeric-looking
and 15 other-label candidates. Each task has 10 sources per source-length tertile.
Labels/strata are provisional metadata, not human validation. Source allocation
covers all 15 families × 3 positions. S180 uses each source once per family/base
slot before position expansion; S540 balances reuse at 6 or 12 attacked cases/source.

| Scenario | Attacked + clean cases | Four-arm invocations | Visible input tokens* | Max output tokens | Model-judge calls** |
|---|---:|---:|---:|---:|---:|
| S180 | 180 + 60 | 960 | 402,288 | 491,520 | 624 |
| S540 | 540 + 60 | 2,400 | 958,440 | 1,228,800 | 1,764 |

*Sum of locally tokenized system and user text, excluding unknown provider framing.
**One judge evaluation per attacked arm routed to model scoring; no actual calls.
Judge prompt/output tokens, prices, quotas, review labor and reserves remain unbudgeted.
Hard-benign approved count is zero; adding up to 24 would add up to 96 target calls.
Original gold invalidity may cause symmetric utility attrition after review. No silent
case replacements or outcome-based exclusions occurred. Manifest/index files record
selected IDs, variants, source reuse and offsets. Full raw cases remain local.

| Candidate | Full cases.jsonl SHA-256 |
|---|---|
| S180 | `fc1f069c22db82f77986bf797caaf0a4241c851edb3ddfe39891cafecd624f46` |
| S540 | `b45410c5c8d4de010289bffd59ccf4c067b02cb109158eebeff136432dfa100f` |

A separate unapproved train-only pilot candidate has 36 attacked + 4 clean cases,
160 four-arm invocations, no shared test sources and no colliding train family.
Its 40 rendered cases were also token-checked and its 160 invocations mock-run;
these are offline pilot-candidate checks, not a live pilot.
No approved hard-benign pilot records exist; pilot gold also needs independent review.

## Token matching — FAIL

Installed tiktoken 0.14.0 maps the exact proposed model name to o200k_base.
The initially tried 0.12.0 did not map that name; no fallback mapping was injected.
Account access is unverified. Vocabulary/rank, regex and cache hashes are preserved
in token summaries. Every planned complete rendered user message was counted,
including all attacked and clean candidate cases. No approved hard-benign messages
exist to count. System/guidance diagnostics and all prompt hashes are also recorded.

| Task/data condition | N-L minus R | N-F minus R |
|---|---:|---:|
| email/attacked | 5 / 6 | 5 |
| email/clean | 6 | 5 |
| table/attacked | 5 / 6 | 5 |
| table/clean | 6 | 5 |

The same delta ranges occur in S180. **240/240 S180 cases and 600/600 S540 cases
fail exact matching.** N-F is always +5; N-L is +6 on clean and +5/+6 on attacked
cases. This also demonstrates why guidance-only/character counts cannot certify
complete-message equality. All failure IDs remain in `token_counts.jsonl`.
B0 is shorter by design and is not a matched control.
All 40/40 train pilot-candidate cases also fail matching; details are in `evidence/pilot_CANDIDATE/`.

No neutral string was revised, no backup evaluated, and no padding or per-case
wording was introduced. Primary candidate 1 remains unchanged and unapproved.
A documented pre-inference backup evaluation or formal amendment plus independent
semantic review is necessary. Existing failures cannot be waived as equality.

## Mock infrastructure and scoring

| Scenario | Planned/recorded | OK | Explicit terminal failures | Missing/duplicate/misattributed |
|---|---:|---:|---|---:|
| S180 | 960/960 | 956 | one each: timeout, empty, truncated, key mismatch | 0/0/0 |
| S540 | 2400/2400 | 2396 | one each: timeout, empty, truncated, key mismatch | 0/0/0 |

Each build deliberately tested retryable errors, delayed/out-of-order replies and
bounded interruption/resumption; four extra attempts per mock plan are recorded.
Wrong-key outputs remain quarantined as error evidence and never become another
case response. Plan/prompt changes and duplicate/foreign IDs are rejected.
Tests additionally cover exhausted transport errors, cancellation, an abrupt
subprocess exit after committed dispatch, and interrupted attempt caps. Successful
and failed terminal records are preserved on resume. Single coordinator/ledger only;
`mock_missingness.json` retains assigned/request/returned/empty/error/truncated/retried
counts by arm, task, condition, family and position; real judge counts are unmeasured.
remote exactly-once execution is not established by a local mock.

All 75 original scorer registrations are verified against inert original registration
functions: 63 model, 5 language, 5 emoji, 2 fuzzy. Exact original judge rubrics, suffix,
newline replacement and chat/nonchat formatting are available offline. No judge code
that imports or calls an API is executed. Language probability >0.7, seeded detector,
emoji existence, and case-sensitive fuzzy partial_ratio >80 are retained.

Original yes-substring parsing and strict whole-output YES/NO/UNKNOWN parsing are
separate. For example `not yes` is compatible=1 and strict=unresolved, never a silently
valid NO. Missing/empty outputs stay unresolved; unknown/malformed judge states remain
explicit. Synthetic fixtures and utility/missingness summaries are preserved.

The legitimate scorer implements conservative provisional space/case/numeric and
explicit set/sequence normalization, plus unknown/refusal candidates. It refuses to
score unvalidated gold by default. Full unit/currency/date, multi-amount completeness,
paraphrases and evasive refusals need a reviewed rubric/manual adjudication; this
package does not claim a validated answer oracle. UC requires correct AND resolved
attack failure; missingness has assigned-denominator conservative bounds.

## Synthetic statistics verification

10,000 seeded Exponential(1) source-cluster multiplier draws per scenario, one weight
per original source within task reused across all its cases/arms/families/positions.
The primary estimate averages the 90 fixed task/family/position paired-cell means
equally. An entirely unscorable cell returns an unresolved estimate; it is not
silently dropped. Manifest-to-outcome completeness can be required explicitly.
Tests verify hand-computed source weights, repeated-row invariance and reproducibility.

Paired contingency, joint/one/neither valid states, equal-cell ASR bounds and difference
bounds, source-level sensitivity interval, first-half CI stability, family dispersion
and leave-one-family-out effects are emitted. Optional two-way source/family bootstrap
is not implemented. Source bootstrap is conditional on selected fixed attack families;
it does not justify unseen-family inference. No synthetic effect/CI is interpreted as
a defense finding, equivalence result, or adequate power proof.

## P0 gates (§14.1)

PASS here means the stated offline evidence passed, not permission to infer.

| Gate | Status | Evidence | Remaining work | Blocks live pilot? |
|---|---|---|---|---|
| P0-A Source/data integrity | **PASS** | input_hashes.json; data tests | near-duplicate identity remains unknown | No, offline portion verified |
| P0-B Role/reminder fidelity | **PASS** | source AST/golden prompt tests; token prompt hashes | provider role acceptance unverified under C | No, offline portion verified |
| P0-C Tokenizer/model access | **FAIL** | */token_counts.jsonl; proposed model mapping verified | exact control match fails; model access/serialization/context limit unverified | Yes |
| P0-D Neutral semantic controls | **BLOCKED** | arms.json; blank independent reviewer CSVs | two independent semantic approvals and adjudication; final strings not frozen | Yes |
| P0-E Gold/hard-benign validity | **BLOCKED** | blank gold/hard-benign review templates | original gold/answerability and normalization review; no qualified hard-benign set | Yes |
| P0-F Identifiers/error paths | **PASS** | runner tests; */mock_summary.json; history and response ledgers | future live adapter requires separate validation | No, offline portion verified |
| P0-G Scorer/judge access | **BLOCKED** | scorer_registry.json; synthetic_scores.json; parser/rule tests | judge deployment/access/budget/raw response audit and funded human review not verified | Yes |
| P0-H Sampling/statistics preregistration | **BLOCKED** | candidate case manifests; SIMULATED_analysis.json | final scenario/seed/sample and preregistration not approved; simulation is not power proof | Yes |
| P0-I Permissions/resources | **BLOCKED** | token/call envelopes in summary; BIPIA LICENSE hash | quota/fee cap, reviewer schedule, dataset rights restrictions and judge resources unverified | Yes |

P0-C is FAIL even though the tokenizer mapping works: exact matching does not.
Model deployment/serialization/truncation adequacy and all human/access approvals
are unverified. No one has provided a successful semantic or gold review.

## Deliverables, deviations and next stage

Source/tests/config, pinned dependency snapshot, executable Windows commands,
both candidate manifests, every-case token deltas, full mock ledgers, synthetic
scoring/statistics, blank two-reviewer/adjudication templates, this report and
`HANDOFF_05B.md` are delivered. `evidence/` contains shareable hashes/IDs and synthetic
material; raw sources/questions/prompts and gold review forms remain in ignored
local `artifacts/`. Dataset-specific rights still need review before redistribution.

The originally missing `(1)` attachment was resolved when the user explicitly linked
the local `04_experiment_design.md`; its preserved copy/hash is the specification.
Other implementation choices: stdlib/SQLite instead of installing the archived ML
stack; candidate seed only; no forced exact token success; zero approved hard-benign
records; no live adapter. These are recorded rather than disguised as passed gates.
The neutral/backups remain pending further offline review; no new defense was added.

**Chat 5B must stop before inference.** Resolve matching, independent semantic/gold
reviews, model/judge access, resource permissions and final preregistration, then
obtain explicit pilot authorization. See the handoff for ordered work and stop rules.
