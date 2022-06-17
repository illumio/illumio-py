# -*- coding: utf-8 -*-

"""This module provides classes related to policy rule sets.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from illumio.util import MutableObject, pce_api
from illumio.policyobjects import LabelSet

from .rule import Rule
from .iptablesrule import IPTablesRule


@dataclass
@pce_api('rule_sets', is_sec_policy=True)
class RuleSet(MutableObject):
    """Provides scope boundaries for security policy rules.

    Usage:
        >>> from illumio import PolicyComputeEngine, RuleSet, LabelSet
        >>> pce = PolicyComputeEngine('my.pce.com')
        >>> pce.set_credentials('api_key_username', 'api_key_secret')
        >>> app_label = pce.labels.create({'key': 'app', 'value': 'App'})
        >>> env_label = pce.labels.create({'key': 'env', 'value': 'Production'})
        >>> loc_label = pce.labels.create({'key': 'loc', 'value': 'AWS'})
        >>> ruleset = RuleSet(
        ...     name='RS-RINGFENCE',
        ...     scopes=[
        ...         LabelSet(
        ...             labels=[app_label, env_label, loc_label]
        ...         )
        ...     ]
        ... )
        >>> ruleset = pce.rule_sets.create(ruleset)
        >>> ruleset
        Ruleset(
            href='/orgs/1/sec_policy/draft/rule_sets/19',
            name='RS-RINGFENCE'
        )
    """
    enabled: bool = None
    scopes: List[LabelSet] = None
    rules: List[Rule] = None
    ip_tables_rules: List[IPTablesRule] = None
