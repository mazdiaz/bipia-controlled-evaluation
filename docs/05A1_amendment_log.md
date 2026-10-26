# Chat 5A.1 amendment log — proposed, pending human approval

Date: 26 October 2026 (Asia/Jakarta). Machine UTC timestamps, old/new full strings,
SHA-256 values and unchanged protocol/reminder hashes are in
`evidence/05A1/amendment_hashes.json`. Catalog file timestamps reflect when each
candidate list was written; the amendment record was prepared afterward. These
are execution records, not a retroactive claim of preregistration or human approval.

The user explicitly authorized offline neutral-wording remediation. The original
protocol remains unchanged and is retained as the historical specification. This
log proposes revised guidance only; the supervisor must accept the revision and
two independent reviewers must re-review all four final strings before freeze.

Predefined eligibility criteria: fluent surface-composition description; no
defense/trust/hierarchy/answer/task-strategy directions; fixed task-substituted
strings; leading space; N-L no parentheses, N-F one parenthetical sentence; prefer
shared words; exact full-user equality everywhere. Only tokenizer/integrity
results were used. No live outputs, ASRs, padding, per-case strings, random search,
or inference were used.

| Attempt in execution order | Full-case mismatches / 880 | N-L delta range | N-F delta range | Decision |
|---|---:|---|---|---|
| Historical primary | 880 | +5,+6 | +5 | reject exact matching |
| Protocol backup | 880 | +2,+3 | +4 | reject exact matching |
| revision_1, shared words/serial comma | 225 | -1,0 | 0 | reject exact matching |
| revision_2, includes instead of contains | 225 | -1,0 | 0 | reject exact matching |
| revision_3, This…other marks | 880 | +1,+2 | +2 | reject exact matching |
| revision_4, colon-compatible N-L | 0 | 0 | 0 | selected for human review |

The first catalog was saved before evaluating its five candidates. After none
passed, round 2 recorded the newline-merging hypothesis and revision_4 before
evaluating it. No candidates beyond these were token-tested. Every exact proposed
string is retained in the two catalog JSONs. Every attempted candidate has 880
per-case count/hash rows in `candidate_<id>_counts.jsonl`, with scenario membership,
task, case type, guidance/full-user counts and deltas, R/context/question hashes.
The 880 rows count scenario memberships; S180/S540 overlap and are not independent
experimental observations. Catalog/result/log files preserve the complete path,
including failed candidates; no outcome-based choice occurred.

Root cause: the primary/backup prose is too long; for N-L a final period followed
by the template colon/newline has a source-dependent merge. `.:\n\n` is one token,
whereas `.:\n` is two. R's parenthetical transition remains two in these examples.
`evidence/05A1/boundary_diagnostics.json` records exact token IDs/pieces. Revision_4
omits N-L's terminal period so the existing colon completes the introduction. Its
comma before `including` and serial comma balance N-F's wrapper; sentence words
are identical. The new strings are in `evidence/05A1/arms.json` and human forms.

Original BIPIA reminder, system/user templates, roles, source files, payloads,
questions, gold, IDs, insertion offsets, seeds, generation parameters and dispatch
order are unchanged. Only N-L/N-F guidance/prompt hashes change in request plans;
token revision metadata and P0-C reporting were updated. All B0/R requests and
nonprompt plan metadata compare identically. Both original case manifests and
the train-only pilot case manifest are byte-identical to prior artifacts and to
fresh regeneration. The 23-file original source audit is identical. See
`integrity_verification.json`; 62 protected prior evidence/specification/report
files remain unchanged.

The revised output lives in `artifacts-05A1/` and `evidence/05A1/`. Do not resume
an old mock ledger with the new prompts: its immutable plan correctly rejects
changed hashes. Original failed reports, counts, logs, ledgers and artifacts stay
in their prior locations. Original 46-test success does not mean old tokens passed.

Tests: new focused assertions first failed (6 failures/8 passes), then passed
(14 passes). The initial expanded suite passed 67 tests; the final suite, including blank-review-state and coverage checks, passed 70 tests. Tests preserve old token
FAIL evidence and verify current full-message equality, tiktoken version, source
AST literals, unchanged B0/R hashes and boundary cases. No formal relaxation of
zero-token matching is proposed. If humans reject these strings and no natural
revision passes both gates, remain NO-GO and seek a formal protocol amendment.
