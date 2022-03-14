# -*- coding: utf-8 -*-

"""This module provides classes related to iptables rules.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from illumio.util import JsonObject, ModifiableObject

from .actor import Actor


@dataclass
class IPTablesStatement(JsonObject):
    table_name: str = None
    chain_name: str = None
    parameters: str = None


@dataclass
class IPTablesRule(ModifiableObject):
    ip_version: str = None
    enabled: bool = None
    statements: List[IPTablesStatement] = None
    actors: List[Actor] = None
