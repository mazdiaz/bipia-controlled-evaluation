import socket
from pathlib import Path
from preflight.pipeline import build
connect = socket.socket.connect
def denied(*args,**kwargs):
    raise RuntimeError('05A1 build prohibits outbound network access')
def local_only(sock,address):
    if isinstance(address,tuple) and address[0] in ('127.0.0.1','::1'):
        return connect(sock,address)
    return denied()
socket.socket.connect=local_only
socket.create_connection=denied
s=build(Path('vendor/BIPIA'),Path('artifacts-05A1'))
print('OFFLINE BUILD COMPLETE',s['recommendation'])
for k,v in s['scenarios'].items():
    print(k,v['tokens']['status'],v['tokens']['mismatched_cases'],v['expected_visible_input_tokens'])
print('pilot',s['pilot_candidate']['tokens']['status'])
