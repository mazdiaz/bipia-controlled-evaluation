# Offline preflight implementation plan

Goal: executable, reproducible offline validation of the four-arm protocol.
Spec: `04_experiment_design.md`, recovered local copy; exact requested `(1)` attachment unavailable.
Architecture: small Python modules, canonical JSON identities, SQLite invocation ledger,
no API client or credentials. Official archive stays outside the research package.
Stack: Python 3.14.0, pytest, tiktoken, NLTK PunktSentenceTokenizer, thefuzz, emoji, langdetect.

Constraints: exact pinned SHA; unchanged reminder/WOSystem; no inference/judge calls;
candidate S180/S540 only; drafts stay unapproved; no invented annotation.

Tasks (each tested before implementation):
- [ ] Source audit/data.py: blob verification, schema/counts, overlaps, split-aware IDs,
  seeded canonical insertion, source-distinct stratified sampling and manifests.
- [ ] prompts.py/tokens.py: source AST golden comparisons, four exact arm strings,
  full-user counts, per-case deltas and hashes; no automatic control revisions.
- [ ] runner.py: SQLite keyed plan/results/history, bounded mocks, out-of-order,
  interruption/resume, timeout/error/empty/truncation, foreign-response rejection.
- [ ] scoring.py/analysis.py: frozen registration export without importing API code,
  original and strict parsing, synthetic rule scoring, conservative utility,
  equal cell weights, task-stratified source bootstrap, missingness and family checks.
- [ ] CLI/reports: reproducible manifests/token/mock/simulation artifacts, empty reviewer
  templates, all P0 gates with evidence and blockers, Windows instructions/handoff.

Review focus: whitespace and Unicode identity; multi-question repeated sources;
wrong-key mock replies; stale ledgers; invalid judge outputs; absent bootstrap cells.
No final sample/seed approval inferred. Seed 20261026 is an engineering candidate.
