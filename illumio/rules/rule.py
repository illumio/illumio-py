from dataclasses import dataclass
from typing import List

from illumio import ModifiableObject
from illumio.util.jsonutils import JsonObject
from illumio.policyobjects import SecurityPrincipal, Service

from .actor import Actor


@dataclass
class LabelResolutionBlock(JsonObject):
    providers: List[str] = None
    consumers: List[str] = None


@dataclass
class Rule(ModifiableObject):
    enabled: bool = None
    ingress_services: List[Service] = None
    resolve_labels_as: LabelResolutionBlock = None
    sec_connect: bool = None
    stateless: bool = None
    machine_auth: bool = None
    providers: List[Actor] = None
    consumers: List[Actor] = None
    consuming_security_principals: List[SecurityPrincipal] = None
    unscoped_consumers: bool = None
    network_type: str = None

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.ingress_services = [Service.from_json(o) for o in self.ingress_services] if self.ingress_services else None
        self.resolve_labels_as = LabelResolutionBlock.from_json(self.resolve_labels_as) if self.resolve_labels_as else None
