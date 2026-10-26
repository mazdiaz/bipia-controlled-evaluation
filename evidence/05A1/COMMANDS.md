# Chat 5A.1 execution register

All commands ran in the existing repository with `.venv/Scripts/python.exe`.
No target/judge/model-access API calls occurred. Public documentation browsing
was limited to official model, model-metadata and rate-limit reference pages.
No credentials were loaded, read, printed or invented.

| Executed command | Actual result/evidence |
|---|---|
| `python -m scripts.audit_05a1_candidates` | Five finite ordered pairs evaluated; all fail. `candidate_execution.txt`, `candidate_results.json`, five per-case files |
| `python -m scripts.audit_05a1_candidates evidence/05A1/candidate_catalog_round2.json` | revision_4 PASS in all 880 scenario memberships. Round-2 execution/results and per-case rows |
| `python -m pytest tests/test_prompts.py tests/test_pipeline.py -q` before renderer changes | 6 failed, 8 passed; `regression_red.txt` |
| Same focused command after renderer changes | 14 passed; `regression_green.txt` |
| `python -m scripts.run_05a1_build` | Complete offline build, both scenarios plus train candidate, mocks and 10,000-draw simulated analyses; exit 0; `build_execution.txt` |
| `python -m pytest -v --junitxml=evidence/05A1/pytest.xml` | 67 passed; `full_pytest.txt`, `pytest.xml` |
| `python -m scripts.prepare_05a1_materials` initial attempt | KeyError on unmapped train pilot scorer; retained `materials_execution_failed.txt` |
| Same materials command after explicitly retaining unresolved pilot judge mapping | PASS integrity/form/envelope generation; `materials_execution.txt`; no invented pilot judge count |
| `python -m pytest -v --junitxml=evidence/05A1/pytest_final.xml` | 70 passed; `full_pytest_final.txt`, `pytest_final.xml` |
| Separate engineering reviewer `python -m pytest tests/test_prompts.py` | 25 passed; limited agent report in `code_review.md`; final agent turn unavailable due model capacity |
| Candidate commands replayed after result-path correction | Exact candidate evidence byte identity; `candidate_replay_execution.txt`, `candidate_replay_verification.json` |
| `git diff --check` | No whitespace errors |

Python one-off local scripts also captured the baseline hash inventory, token
boundary diagnostics, amendment hashes, source/manifest/plan comparisons and
Markdown report/checklist. These used local inputs only. The materials script
compares a fresh case/plan regeneration byte-for-byte against current artifacts,
compares all full case bytes against historical artifacts and every B0/R request
and nonprompt field against the original plan.

Historical results, including original 46-test pass and all failed token counts,
remain in original evidence paths. Reports written for this task use new names;
new execution outputs use `evidence/05A1/` and `artifacts-05A1/`.
