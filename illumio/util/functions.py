# -*- coding: utf-8 -*-

"""This module provides helper functions and decorators for common use-cases.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
import functools
import typing
import warnings

from illumio._version import version
from .constants import ACTIVE, DRAFT, PCE_APIS


def ignore_empty_keys(o):
    return {k: v for (k, v) in o if v is not None}


def convert_draft_href_to_active(href: str) -> str:
    return href.replace('/{}/'.format(DRAFT), '/{}/'.format(ACTIVE))


def convert_active_href_to_draft(href: str) -> str:
    return href.replace('/{}/'.format(ACTIVE), '/{}/'.format(DRAFT))


def deprecated(deprecated_in, message=None):
    """
    Deprecation decorator, adapted from https://stackoverflow.com/a/30253848
    Will emit a warning when the decorated function is called.
    """
    def _deprecated(func):
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


def pce_api(name: str, endpoint: str = None, is_sec_policy=False):
    """Decorates an IllumioObject subclass to denote it as a PCE API object type.

    This registers the type in the PCE_APIS mapping used to determine whether
    a given name corresponds to an API-accessible type.

    We can then leverage __getattr__ to instantiate a generic API interface for
    any registered type (with some caveats, see the _PCEObjectAPI documentation).

    By default, registers the endpoint as /{name}, but the endpoint can also be
    specified in the decorator function call.

    For example:

    >>> @pce_api('labels', endpoint='/labels')
    >>> class Label(IllumioObject):
    ...     ...
    >>> pce = PolicyComputeEngine(...)
    >>> # the 'labels' name is registered, and so we can
    >>> # call /labels endpoints through the _PCEObjectAPI interface
    >>> labels = pce.labels.get()
    >>> labels
    [
        Label(
            href='/orgs/1/labels/1',
            key='role',
            value='R-DB',
            ...
        ),
        ...
    ]

    Args:
        name (str): the name of the API. used as a PolicyComputeEngine attribute name
            to generate the API interface.
        endpoint (str, optional): _description_. Defaults to None.
        is_sec_policy (bool, optional): whether or not the object reflects a security policy
            API with the sec_policy/{pversion} prefix. Defaults to False.
    """
    def _decorator(cls):
        PCE_APIS[name] = (endpoint or '/{}'.format(name), cls, is_sec_policy)
        return cls
    return _decorator


def parse_url(url: str) -> tuple:
    protocol = None
    url = url.strip()        # remove leading/trailing whitespace
    if '://' in url:         # use provided protocol if included
        protocol, url = url.split('://')
    if protocol not in ('http', 'https'):
        protocol = 'https'   # only support http(s)
    url = url.split('/')[0]  # remove any provided path
    return protocol, url


if hasattr(typing, 'get_origin'):
    # python 3.8+ - introduces the get_origin function
    def isunion(type_):
        return typing.get_origin(type_) is typing.Union

    def islist(type_):
        if type_ is list:
            return True
        return typing.get_origin(type_) is list

elif hasattr(typing, '_GenericAlias'):
    # python 3.7 - changes meta types to be based off the
    # _GenericAlias supertype. __extra__ is now __origin__
    def isunion(type_):
        if isinstance(type_, typing._GenericAlias):
            return type_.__origin__ is typing.Union
        return False

    def islist(type_):
        if type_ is list:
            return True
        if isinstance(type_, typing._GenericAlias):
            return type_.__origin__ is list
        return False

else:
    # python 3.6
    def isunion(type_):
        return isinstance(type_, typing._Union)

    def islist(type_):
        if type_ is list:
            return True
        # in 3.6, List's type is GenericMeta, so we
        # instead check the __extra__ param
        if hasattr(type_, '__extra__'):
            return type_.__extra__ is list
        return False
