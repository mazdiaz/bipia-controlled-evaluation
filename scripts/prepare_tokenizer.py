"""One-time public rank download; never calls a model/API."""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from preflight.tokens import encoding

enc = encoding()
print('Verified proposed model encoding:',enc.name)
