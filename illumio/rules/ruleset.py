from dataclasses import dataclass
from typing import List

from illumio.util import ModifiableObject
from illumio.policyobjects import LabelSet

from .rule import Rule
from .iptablesrule import IPTablesRule


@dataclass
class Ruleset(ModifiableObject):
    enabled: bool = None
    scopes: List[LabelSet] = None
    rules: List[Rule] = None
    ip_tables_rules: List[IPTablesRule] = None
