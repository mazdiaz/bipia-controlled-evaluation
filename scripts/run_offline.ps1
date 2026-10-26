$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force evidence | Out-Null
$python = Join-Path (Get-Location) '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Create .venv and install requirements-lock.txt first; see README.md.'
}
Start-Transcript -Path evidence/reproduction_transcript.txt -Force
try {
    & $python -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed' }
    & $python -m pytest -v --junitxml=evidence/pytest.xml 2>&1 | Tee-Object -FilePath evidence/final_pytest.txt
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    & $python -m preflight --out artifacts 2>&1 | Tee-Object -FilePath evidence/final_preflight.txt
    if ($LASTEXITCODE -ne 0) { throw 'Artifact build failed' }
    & $python scripts/publish_evidence.py
    if ($LASTEXITCODE -ne 0) { throw 'Evidence publishing failed' }
    Write-Output 'Offline build finished. Read artifacts/summary.json for gate status; successful execution is not pilot approval.'
} finally {
    Stop-Transcript
}
