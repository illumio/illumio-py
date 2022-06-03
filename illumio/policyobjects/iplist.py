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
    ip_ranges: List[IPRange] = None
    fqdns: List[FQDN] = None
