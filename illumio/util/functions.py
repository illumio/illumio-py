import socket


def convert_protocol(protocol: str) -> int:
    return socket.getprotobyname(protocol)


def ignore_empty_keys(o):
    return {k: v for (k, v) in o if v is not None}
