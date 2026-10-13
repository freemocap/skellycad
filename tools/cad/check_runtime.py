"""Reject a live RPC endpoint owned by a different workspace."""
from pathlib import Path
import xmlrpc.client

ROOT = Path(__file__).resolve().parents[2]


class TimeoutTransport(xmlrpc.client.Transport):
    def make_connection(self, host):
        connection = super().make_connection(host)
        connection.timeout = 5
        return connection


def check():
    with xmlrpc.client.ServerProxy('http://127.0.0.1:9875', transport=TimeoutTransport(), allow_none=True) as server:
        identity = server.cad_runtime_identity()
    if Path(identity['root']).resolve() != ROOT:
        raise RuntimeError(f"Port 9875 belongs to {identity['root']}; preserve that session and resolve ownership first.")
    return identity


if __name__ == '__main__':
    print(check())
