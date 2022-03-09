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
