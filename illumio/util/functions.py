import functools
import socket
import warnings

from illumio._version import version
from .constants import ACTIVE, DRAFT


def convert_protocol(protocol: str) -> int:
    return socket.getprotobyname(protocol)


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
