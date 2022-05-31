# -*- coding: utf-8 -*-

"""This module provides classes related to policy rule sets.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from illumio.util import ModifiableObject, pce_api
from illumio.policyobjects import LabelSet

from .rule import Rule
from .iptablesrule import IPTablesRule


@dataclass
@pce_api('rule_sets', is_sec_policy=True)
class RuleSet(ModifiableObject):
    enabled: bool = None
    scopes: List[LabelSet] = None
    rules: List[Rule] = None
    ip_tables_rules: List[IPTablesRule] = None
