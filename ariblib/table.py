import itertools

from ariblib import packet

_tables = {}


def on(pids, table_ids):
    def wrapper(func):
        for pid, table_id in itertools.product(pids, table_ids):
            _tables[(pid, table_id)] = func
        return func
    return wrapper


def run(f):
    for pid, table_id, payload in packet.payloads(packet.packets(f)):
        if (pid, table_id) in _tables:
            _tables[(pid, table_id)](payload)


def tables(pids, table_ids, payloads):
    return (payload for pid, table_id, payload in payloads
            if pid in pids and table_id in table_ids)
