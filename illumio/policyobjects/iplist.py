from dataclasses import dataclass
from typing import List

from illumio.util import JsonObject, ModifiableObject


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
class IPList(ModifiableObject):
    ip_ranges: List[IPRange] = None
    fqdns: List[FQDN] = None

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.ip_ranges = [IPRange.from_json(o) for o in self.ip_ranges] if self.ip_ranges else None
        self.fqdns = [FQDN.from_json(o) for o in self.fqdns] if self.fqdns else None
