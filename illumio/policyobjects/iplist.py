# -*- coding: utf-8 -*-

"""This module provides classes related to IP list policy objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from illumio.util import JsonObject, MutableObject, pce_api


@dataclass
class IPRange(JsonObject):
    description: str = None
    from_ip: str = None
    to_ip: str = None
    exclusion: bool = None


@dataclass
class FQDN(JsonObject):
    fqdn: str = None
    description: str = None


@dataclass
@pce_api('ip_lists', is_sec_policy=True)
class IPList(MutableObject):
    """Represents an IP list in the PCE.

    IP lists are list of IP addresses, subnets, CIDR blocks, and/or FQDNs.
    They can be used in conjunction with other security policy objects to
    allow or deny traffic from these defined ranges.

    See https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/ip-lists.htm

    Usage:
        >>> from illumio import PolicyComputeEngine, IPList, IPRange
        >>> pce = PolicyComputeEngine('my.pce.com')
        >>> pce.set_credentials('api_key_username', 'api_key_secret')
        >>> ip_list = IPList(
        ...     name='IPL-INTERNAL',
        ...     ip_ranges=IPRange(
        ...         from_ip='192.168.0.0/16'
        ...     )
        ... )
        >>> ip_list = pce.ip_lists.create(ip_list)
        >>> ip_list
        IPList(
            href='/orgs/1/sec_policy/draft/ip_lists/22',
            name='IPL-INTERNAL',
            ip_ranges=IPRange(
                from_ip='192.168.0.0/16'
            ),
            ...
        )
    """
    ip_ranges: List[IPRange] = None
    fqdns: List[FQDN] = None
