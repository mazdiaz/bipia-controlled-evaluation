# Complete token-equivalence report — revision 4

tiktoken 0.14.0; verified model mapping o200k_base. Entire rendered user messages counted, system tokens recorded separately. B0 is intentionally unmatched. All human control approvals remain PENDING.

| Candidate/task/type | Cases | N-L minus R | N-F minus R | B0 user range | N-L = N-F = R user range |
|---|---:|---|---|---|---|
| S180/email/attacked | 90 | [0] | [0] | [116, 336] | [133, 353] |
| S180/email/clean | 30 | [0] | [0] | [109, 329] | [126, 346] |
| S180/table/attacked | 90 | [0] | [0] | [248, 918] | [265, 935] |
| S180/table/clean | 30 | [0] | [0] | [232, 905] | [249, 922] |
| S540/email/attacked | 270 | [0] | [0] | [119, 345] | [136, 362] |
| S540/email/clean | 30 | [0] | [0] | [109, 329] | [126, 346] |
| S540/table/attacked | 270 | [0] | [0] | [245, 933] | [262, 950] |
| S540/table/clean | 30 | [0] | [0] | [232, 918] | [249, 935] |
| pilot_CANDIDATE/email/attacked | 18 | [0] | [0] | [216, 273] | [233, 290] |
| pilot_CANDIDATE/email/clean | 2 | [0] | [0] | [206, 260] | [223, 277] |
| pilot_CANDIDATE/table/attacked | 18 | [0] | [0] | [498, 951] | [515, 968] |
| pilot_CANDIDATE/table/clean | 2 | [0] | [0] | [488, 932] | [505, 949] |

The token summary JSONs record rank/vocabulary, regex, cache hashes, version, mapping and account-access caveat. Per-case counts for all four arms, full prompt SHA-256, context/question SHA-256, task/type and deltas are in:

- `S180/token_counts.jsonl`: 240 cases (180 attacked, 60 clean).
- `S540/token_counts.jsonl`: 600 cases (540 attacked, 60 clean).
- `pilot_CANDIDATE/token_counts.jsonl`: 40 train-only cases (36 attacked, 4 clean).

Paths above are relative to `evidence/05A1/`. There are 880 scenario-membership rows; overlapping alternatives are not independent cases. Zero approved hard-benign rows exist; any later addition requires new counts.

Historical primary/backup and four revisions have complete per-case attempts in `candidate_<id>_counts.jsonl`. See `candidate_results.json`, `candidate_catalog_round2_results.json` and the amendment log for selection chronology. Guidance-only diagnostics did not determine equality.

This proves offline text-token equality for the checked prompts, not account access, provider framing equality, semantic neutrality, or efficacy.
