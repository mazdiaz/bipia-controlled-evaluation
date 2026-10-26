import socket
import pytest


@pytest.fixture(autouse=True)
def deny_test_network(monkeypatch):
    original_connect = socket.socket.connect
    def denied(*args,**kwargs):
        raise AssertionError('Tests are offline; prepare the public tokenizer cache before pytest')
    def external_denied(sock,address):
        # Windows asyncio implements its internal socketpair via loopback.
        if isinstance(address,tuple) and address[0] in ('127.0.0.1','::1'):
            return original_connect(sock,address)
        return denied()
    monkeypatch.setattr(socket.socket,'connect',external_denied)
    monkeypatch.setattr(socket,'create_connection',denied)
