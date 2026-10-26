# Execution command record

Working directory for these commands:
`C:\Users\diazh\OneDrive\文档\bipia-controlled-evaluation`

These are the implementation, acquisition and validation commands actually executed.
Read-only inspection also used `Get-Content`, `Get-ChildItem`, `rg`, `git show`,
`git diff`, `git ls-files`, and local Python schema/count inspection.
No target model/judge command, credential lookup or experiment was executed.

## Acquisition and environment

```powershell
python --version
git --version
git clone https://github.com/microsoft/BIPIA.git vendor/BIPIA
git -C vendor/BIPIA checkout --detach a004b69ec0dd446e0afd461d98cb5e96e120a5d0
git -C vendor/BIPIA rev-parse HEAD
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest==8.4.2 tiktoken==0.12.0 nltk==3.9.2 langdetect==1.0.9 fuzzywuzzy==0.18.0
.\.venv\Scripts\python.exe -m pip uninstall -y fuzzywuzzy
.\.venv\Scripts\python.exe -m pip install thefuzz==0.22.1 emoji==2.15.0
.\.venv\Scripts\python.exe -m pip index versions tiktoken
.\.venv\Scripts\python.exe -m pip install tiktoken==0.14.0
```

Thefuzz is the actual upstream fuzzy dependency. The initial tiktoken version did
not map the proposed model name; 0.14.0 did. Initial pip output hit Windows console
encoding logging errors while installing 0.14.0; subsequent import/version/tests and
pip check confirm the installation. Later commands set UTF-8 explicitly.

Checkout canonicalization/version control commands:

```powershell
git init -b offline-preflight
git -C vendor/BIPIA config core.autocrlf false
git -C vendor/BIPIA checkout-index --all --force
```

The existing index/stat cache kept CRLF checkouts, so the audited files were then
restored from pinned blob bytes, with this exact local command:

```powershell
.\.venv\Scripts\python.exe -c "from preflight.data import SOURCE_FILES,blob; from pathlib import Path; p=Path('vendor/BIPIA'); [(p/f).write_bytes(blob(p,f)) for f in SOURCE_FILES]"
.\.venv\Scripts\python.exe -c "from preflight.data import SOURCE_FILES; import subprocess; subprocess.run(['git','-C','vendor/BIPIA','add','--',*SOURCE_FILES],check=True)"
git -C vendor/BIPIA status --short
```

The final archive status is clean, with no staged or unstaged source changes.
New clones should use the supplied fetch script, which disables autocrlf initially.

## Test commands and evidence

The numbered files preserve real intermediate failures and successful runs.
Output was captured using `*> evidence/NAME.txt` followed by `Get-Content -Tail`.
One first data run was interrupted after detecting per-row subprocess overhead;
the loader was corrected to resolve each file's blob ID once. A duplicate attempt
to write its still-open log failed without running another test process.

| Command after `.\.venv\Scripts\python.exe` | Evidence file(s) | Observed outcome |
|---|---|---|
| `-m pytest tests/test_data.py -q` | 01, 02, 03, 04, 05 | Missing implementation; interrupted run; concrete implementation failures; then 14 passed |
| `-m pytest tests/test_prompts.py -q` | 06, 07, 08 | Missing implementation; mapping failure with 0.12.0; then 4 passed with 0.14.0 |
| `-m pytest tests/test_runner.py -q` | 09, 10, 11 | Missing implementation; too-tight Windows timeout fixture; then 4 passed |
| `-m pytest tests/test_scoring_analysis.py -q` | 12, 13 | Missing implementation; then 14 passed |
| `-m pytest tests/test_pipeline.py -q` | 14 | Missing implementation |
| `-m pytest -q` | 15, 17 | Missing import/new checkout-hash failures; then 40 passed |
| `-m pytest tests/test_extra_integrity.py -q` | 20 | 3 passed |
| `-m pytest tests/test_scoring_analysis.py -q` | 21, 22 | Missing judge renderer; then 15 passed |
| `-m pytest -v --junitxml=evidence/pytest.xml` | 25, 27 | Outbound-socket blocker initially blocked Windows internal socketpair; allow loopback; then 45 passed |
| `-m pytest tests/test_pipeline.py -q` | 28 | New pilot token/accounting checks failed before implementation |
| `-m pytest -v --junitxml=evidence/pytest.xml` | 29, final_pytest.txt | **46 passed in 10.85s** |

Full filenames are visible in `evidence/`. `03_data_tests.txt` has source-data argument
repr lines redacted in the shareable copy; its unmodified output remains local at
`artifacts/evidence_raw/03_data_tests.txt`. This does not change test errors/results.

## Artifact execution and final checks

```powershell
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe -m preflight
.\.venv\Scripts\python.exe -m pip freeze > requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/fetch_source.py
.\.venv\Scripts\python.exe scripts/prepare_tokenizer.py
.\.venv\Scripts\python.exe -m pytest -v --junitxml=evidence/pytest.xml
.\.venv\Scripts\python.exe -m preflight
.\.venv\Scripts\python.exe scripts/publish_evidence.py
```

Artifact executions were captured as `16_preflight_run.txt` (failed missing import),
`18_preflight_run.txt` (completed), `26_final_preflight.txt` (completed), and
`30_final_preflight.txt` / `final_preflight.txt` (completed with additional pilot/mock
accounting). Successful builds report NO-GO, not permission to start inference.
Source/tokenizer/pip checks are recorded in 19, 23 and 24. A separate reviewer also
ran 18 targeted tests successfully; see `code_review.md` for scope.

To repeat setup and checks without the development failures, use README.md or
`scripts/run_offline.ps1`. The wrapper itself is supplied for convenience; the
individual Python commands above were the executed validation path.
