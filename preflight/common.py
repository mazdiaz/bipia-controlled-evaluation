import hashlib
import json
from pathlib import Path

COMMIT = 'a004b69ec0dd446e0afd461d98cb5e96e120a5d0'
MODEL = 'gpt-5.4-mini-2026-03-17'
SEED = 20261026


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    if not isinstance(value, (str, bytes)):
        value = canonical(value)
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value)+'\n', encoding='utf-8', newline='\n')


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(canonical(row)+'\n')
