# Independent review packet — 05A1-v1

Prepared 26 October 2026 (Asia/Jakarta). **All human decisions are pending.**
Offline token equality is established for candidate lists only. It says nothing
about semantic inertness, gold validity, efficacy, or authorization to infer.

The coordinator assigns two anonymous raters who did not craft the controls.
Raters complete separate copies without discussing judgments or seeing the other
form, model outputs, arm outcomes, ASRs, or automated answer scores. Semantic
forms necessarily show control labels; gold review is independent of treatment.
Use UTC timestamps and a stable reviewer ID. Record a reason/evidence for every
decision. Preserve submitted files, compute SHA-256, then adjudicate disagreements
in `forms/adjudication.csv`; never overwrite an independent submission.

Use these packets in order:

1. [Semantic neutrality](semantic_neutrality.md): four task/control rows in each
   `forms/semantic_reviewer_1.csv` and `_2.csv`. Synthetic examples only.
2. [EmailQA gold and unknown](email_gold_unknown.md): 32 unique selected base
   records across both scenario alternatives and the train pilot. Two forms.
3. [TableQA normalization](table_normalization.md): 50 unique selected base
   records across those alternatives. Two forms.
4. [Hard-benign eligibility](hard_benign.md): construction form and two blank
   reviewer forms. No real candidates have been constructed or approved.

CSV metadata is populated; **judgment, reviewer and approval fields are blank**.
The gold forms reference local restricted JSONL records in
`artifacts-05A1/review_packets/email_source_records.jsonl` and
`table_source_records.jsonl`. Join on `base_id`, not row order. Each includes the
original context, question and gold; hashes must equal the CSV. `scenarios` lists
all memberships. One adjudicated base ruling applies consistently to every
derived case and arm. The S180/S540 alternatives have overlapping and different
bases; do not assume reviewing one fully covers the other. There are 82 unique
bases in the union, not a proposal to run both alternatives.

The generator reuses `preflight.pipeline.csv_template` and extends the existing
annotation schema with explicit protocol questions. Original annotation files
remain in `artifacts/annotations/`. Raw source records are Git-ignored and should
be shared only through approved restricted channels. The committed forms contain
IDs/hashes, with benign synthetic text in semantic forms.

No software here consumes completed forms to grant live permission. The
coordinator must check completeness, reviewer independence, all required criteria,
adjudication and signed freeze manually. A changed wording, context or rubric
invalidates the affected approvals and requires a new version/hash and fresh
review. Ambiguous or invalid gold stays unresolved until a documented pre-output
decision; exclusions apply symmetrically and retain original IDs and reasons.

Examples in these packets are **synthetic training examples with suggested
rubric interpretations**, not human judgments on any study record.
