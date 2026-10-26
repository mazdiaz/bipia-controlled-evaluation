# BIPIA offline thesis preflight

**NO-GO for a live pilot.** The unchanged draft neutral controls fail exact token
matching. This package implements offline infrastructure; no target model or judge
was called. See [05_preflight_report.md](05_preflight_report.md) for measured results
and [HANDOFF_05B.md](HANDOFF_05B.md) for the remaining gates.

The user-linked [protocol](docs/04_experiment_design.md) is authoritative for study
requirements. The assignment's offline-only authorization governs execution.
Source: [Microsoft BIPIA pinned revision](https://github.com/microsoft/BIPIA/tree/a004b69ec0dd446e0afd461d98cb5e96e120a5d0).
The archived benchmark is not installed; its model/API imports are never run.

## Reproduce on Windows PowerShell

Tested with **Python 3.14.0**, Git 2.51.2.windows.1, Windows, UTF-8. Run from this
project directory. Do not set API credentials; none are needed.

```powershell
$env:PYTHONUTF8 = '1'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts/fetch_source.py
.\.venv\Scripts\python.exe scripts/prepare_tokenizer.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -v --junitxml=evidence/pytest.xml
.\.venv\Scripts\python.exe -m preflight --out artifacts
```

Installation, Git acquisition and the first public tokenizer-rank download require
Internet access. After preparation, tests and artifact generation work offline.
NLTK uses an untrained `PunktSentenceTokenizer()` exactly as pinned BIPIA does;
**no NLTK corpus download is needed**. Tests deny outbound sockets, allowing only
loopback needed by Windows asyncio's internal socketpair. No test uses live APIs.

For transcript capture after setup:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_offline.ps1
```

WSL uses the same pinned requirements (not separately verified here):

```bash
python3 -m venv .venv-wsl
.venv-wsl/bin/python -m pip install -r requirements-lock.txt
.venv-wsl/bin/python scripts/fetch_source.py
.venv-wsl/bin/python scripts/prepare_tokenizer.py
.venv-wsl/bin/python -m pytest -v
.venv-wsl/bin/python -m preflight --out artifacts-wsl
```

If acquisition fails, preserve the error and retry those same acquisition commands.
Do not substitute mirror datasets. `--repo PATH` supports an existing verifiable
pinned clone. A mismatched commit is rejected. Canonical Git blobs are the loader's
inputs; the audit records both blob and checkout byte hashes. Windows autocrlf can
make checkout hashes differ: clone initially with `--config core.autocrlf=false` as
the supplied fetch script does. Do not rewrite a working repository with user edits.

## Commands and layout

`python -m preflight --help` lists options. Default: both scenarios, 10,000 bootstrap
draws, all case/arm mock invocations. `--bootstrap-repetitions 20 --no-mock --out
artifacts-quick` is a faster partial build; it does not establish P0-F in that build.
The CLI's zero exit code means artifact generation succeeded; read gate status in
`summary.json`. Token failure is an intended measured outcome, not a reason to hide
the generated mismatch rows. There is no live-inference command.

| Location | Contents |
|---|---|
| `preflight/data.py` | Pinned blob loading, hashes, overlap crosswalk, insertion, source sampling |
| `preflight/prompts.py`, `tokens.py` | Four arms, exact templates, complete rendered message counts |
| `preflight/runner.py` | SQLite keyed mock plan, attempts, explicit failures and resume |
| `preflight/scoring.py`, `analysis.py` | Original-compatible/strict scoring, candidate gold rubric, clustered analysis |
| `preflight/pipeline.py` | Rebuild all local artifacts and blank review templates |
| `tests/` | Unit, integration, process-exit and offline integrity tests |
| `config/analysis_config.json` | Candidate settings, not approved preregistration |
| `evidence/` | Actual test logs, command record, shareable summaries and indexes |
| `artifacts/` | Local full cases, prompts, mocks, annotations and simulations; Git-ignored |
| `vendor/BIPIA/` | Original archive at the pinned commit; Git-ignored |
| `.tokenizer-cache/` | Public tokenizer ranks; Git-ignored; hashes recorded |

Each scenario folder contains `cases.jsonl`, `case_index.jsonl`,
`generation_plan.jsonl`, `token_counts.jsonl`, `token_summary.json`,
`mock.sqlite`, `mock_responses.jsonl`, `mock_history.jsonl`, `mock_summary.json`,
`SIMULATED_outcomes.jsonl`, and `SIMULATED_analysis.json`.
Top-level artifacts include `input_hashes.json`, `scorer_registry.json`, `arms.json`,
`synthetic_scores.json`, `summary.json`, train-only pilot candidate cases/plans, and
`annotations/` CSVs. Exact original strings are retained locally in case files.

IDs/hash outputs, sampled cases, token measurements and seeded simulations reproduce
with the pinned environment. Wall-clock event timestamps, SQLite bytes and run/resume
diagnostics are not byte-deterministic. Both scenarios remain **candidates** with
engineering seed `20261026`. No hard-benign case or final sample is approved.

The ledger is for one coordinator per database. Rerunning the same plan skips terminal
records and resumes pending/interrupted requests under a total three-attempt cap.
A changed plan is rejected; use a separate output directory for a changed plan.
Failed terminal records stay explicit and are not automatically retried until success.
Mock process recovery does not establish provider-side exactly-once execution.

## Review and research boundaries

Read [annotation_rubric.md](docs/annotation_rubric.md). Two independent reviewer CSVs
have blank judgments. The gold scorer is a conservative provisional normalization
tool, not a verified semantic oracle. `validated=True` in synthetic tests does not
certify any real gold answer. Hard-benign construction/approval and human audit remain
manual, documented stages. Source-only uncertainty is conditional on the 15 fixed
attack families. Simulated effects are engineering checks, never thesis findings.

Draft controls are unchanged, unreviewed and unmatched. There was no padding, wording
search, attack-output optimization, replacement model, or boundary-marker arm.
`gpt-5.4-mini-2026-03-17` remains a proposal, not proof of account access.
Provider context capacity, request support, hidden wrappers and output adequacy remain
unverified. There is no automatic truncation or message shortening.

BIPIA code excerpts retain Microsoft attribution and the full original license in
[THIRD_PARTY_BIPIA_LICENSE.txt](THIRD_PARTY_BIPIA_LICENSE.txt). That license explicitly
lists separate dataset licenses. Keep personal-looking raw emails/local prompt files
restricted; verify dataset-specific redistribution obligations before release.
Only hashes/indexes and synthetic material are committed as evidence here.
