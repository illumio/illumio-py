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
    caps: List[str] = None

    def _decode_complex_types(self) -> None:
        super()._decode_complex_types()
        self.scopes = [LabelSet.from_json(o) for o in self.scopes] if self.scopes else None
        self.rules = [Rule.from_json(o) for o in self.rules] if self.rules else None
        self.ip_tables_rules = [IPTablesRule.from_json(o) for o in self.ip_tables_rules] if self.ip_tables_rules else None
