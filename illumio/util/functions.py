import socket

from .constants import ACTIVE, DRAFT


def convert_protocol(protocol: str) -> int:
    return socket.getprotobyname(protocol)


def ignore_empty_keys(o):
    return {k: v for (k, v) in o if v is not None}


def convert_draft_href_to_active(href: str) -> str:
    return href.replace('/{}/'.format(DRAFT), '/{}/'.format(ACTIVE))
