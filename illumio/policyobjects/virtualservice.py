from dataclasses import dataclass
from typing import List

from .policyobject import PolicyObject
from .serviceport import ServicePort


@dataclass
class VirtualService(PolicyObject):
    name: str
    service_ports: List[ServicePort]

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "service_ports": [sp.to_json() for sp in self.service_ports]
        }
