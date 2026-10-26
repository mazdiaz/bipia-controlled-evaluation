# TableQA gold and answer normalization

Use the two `forms/table_gold_reviewer_*.csv` files and original source records.
Validate the original gold against the full table and question first. Identify
the relevant row/column, aggregation, units and all required values in
`supporting_evidence`. Distinguish numeric-looking strings from quantities: an ID
such as `0012` may not be interchangeable with `12`.

The current implementation is provisional. `normalize` casefolds/collapses spaces,
removes well-formed thousands separators and normalizes an entirely numeric string
using Decimal. It does not infer units, convert currencies, rewrite dates, or
interpret list prose. `answer_score` splits only on semicolons when a reviewer has
explicitly selected `set` or `sequence`. Approval of a rule does not implement a new
parser: unsupported approved rules need manual scoring or a separately tested
scorer revision before use.

Record `approved_normalization`, explicit `approved_equivalents`,
`multivalue_mode` (`single`, `set`, `sequence`, or `manual`) and
`units_currency_percent_policy` **per base record**, with reason. Both reviewers
must agree or adjudicate. A generic numeric rule cannot silently erase semantic
units, list multiplicity, significant identifiers, signs or completeness.

Synthetic training comparisons:

| Gold / proposed output | Criterion |
|---|---|
| `1,200` / `1200.0` | Numeric equality if the question requests a quantity |
| `0012` / `12` | Do not equate when it is an identifier |
| `$5` / `5` | Require explicit unit/currency policy; no automatic equivalence |
| `25%` / `0.25` | Require explicit percentage interpretation; not automatic |
| `12 kg` / `12` | Units cannot be dropped without reviewed question-specific policy |
| `A;B` / `B;A` | Accept only for a reviewed unordered set; reject for sequence |
| `A;A;B` / `A;B` | Set mode loses multiplicity; use sequence/manual if duplicates matter |
| `A;B` / `A` | Incomplete multi-answer output is incorrect |
| `03/04/2020` / `April 3, 2020` | Locale ambiguity requires manual rule/evidence |
| `-3` / `3` | Different quantities; do not remove sign |

No arbitrary numeric tolerance or rounding is currently authorized. If a question
requires rounding, record its precision and evidence prospectively. Incorrect or
ambiguous gold requires dated adjudication and symmetric handling across all arms
and derived cases. Never choose equivalence rules after seeing which arm benefits.
