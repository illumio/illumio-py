from typing import Union

from .constants import Protocol

from illumio import IllumioException


def convert_protocol(protocol: Union[str, int]) -> int:
    try:
        proto = Protocol(protocol) if type(protocol) is int else Protocol[protocol.upper()]
        return proto.value
    except:
        raise IllumioException("Unknown or invalid protocol: {0}".format(protocol))


def ignore_empty_keys(o):
    return {k: v for (k, v) in o if v is not None}
