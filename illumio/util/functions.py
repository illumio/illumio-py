# -*- coding: utf-8 -*-

"""This module provides helper functions and decorators for common use-cases.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
import functools
import socket
import warnings

from illumio._version import version
from .constants import ACTIVE, DRAFT


def ignore_empty_keys(o):
    return {k: v for (k, v) in o if v is not None}


def convert_draft_href_to_active(href: str) -> str:
    return href.replace('/{}/'.format(DRAFT), '/{}/'.format(ACTIVE))


def convert_active_href_to_draft(href: str) -> str:
    return href.replace('/{}/'.format(ACTIVE), '/{}/'.format(DRAFT))


def deprecated(deprecated_in, message=None):
    def _deprecated(func):
        """
        Deprecation decorator, adapted from https://stackoverflow.com/a/30253848
        Will emit a warning when the decorated function is called.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            default_message = "Call to deprecated function {}. Deprecated in version {}, current version is {}.".format(
                func.__name__, deprecated_in, version
            )
            warning_message = message or default_message
            warnings.warn(warning_message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return _deprecated


def parse_url(url: str) -> tuple:
    protocol = None
    url = url.strip()        # remove leading/trailing whitespace
    if '://' in url:         # use provided protocol if included
        protocol, url = url.split('://')
    if protocol not in ('http', 'https'):
        protocol = 'https'   # only support http(s)
    url = url.split('/')[0]  # remove any provided path
    return protocol, url


@deprecated(deprecated_in='0.8.2')
def convert_protocol(protocol: str) -> int:
    """DEPRECATED (v0.8.2). Protocol conversion is baked into service creation.

    Given a protocol name, returns the integer ID of that protocol.

    Usage:
        >>> convert_protocol('tcp')
        6

    Args:
        protocol (str): case-insensitive protocol string, e.g. 'tcp', 'UDP'

    Returns:
        int: the integer ID of the given protocol, e.g. 17 for 'udp'
    """
    return socket.getprotobyname(protocol)
