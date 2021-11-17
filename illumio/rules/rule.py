from dataclasses import dataclass
from typing import List

from illumio.util import JsonObject, Reference, ModifiableObject

from .actor import Actor


@dataclass
class LabelResolutionBlock(JsonObject):
    providers: List[str] = None
    consumers: List[str] = None


@dataclass
class Rule(ModifiableObject):
    enabled: bool = None
    ingress_services: List[Reference] = None
    resolve_labels_as: LabelResolutionBlock = None
    sec_connect: bool = None
    stateless: bool = None
    machine_auth: bool = None
    providers: List[Actor] = None
    consumers: List[Actor] = None
    consuming_security_principals: List[Reference] = None
    unscoped_consumers: bool = None
    network_type: str = None

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.ingress_services = [Reference.from_json(o) for o in self.ingress_services] if self.ingress_services else None
        self.resolve_labels_as = LabelResolutionBlock.from_json(self.resolve_labels_as) if self.resolve_labels_as else None
        self.providers = [Actor.from_json(o) for o in self.providers] if self.providers else None
        self.consumers = [Actor.from_json(o) for o in self.consumers] if self.consumers else None
        self.consuming_security_principals = [Reference.from_json(o) for o in self.consuming_security_principals] if self.consuming_security_principals else None