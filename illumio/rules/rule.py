from dataclasses import dataclass
from typing import List, Union

from illumio.util import JsonObject, Reference, ModifiableObject
from illumio.policyobjects import Service, ServicePort

from .actor import Actor


@dataclass
class BaseRule(ModifiableObject):
    ingress_services: List[Union[Service, ServicePort]] = None
    providers: List[Actor] = None
    consumers: List[Actor] = None

    def _decode_complex_types(self):
        super()._decode_complex_types()
        decoded_ingress_services = []
        for service in self.ingress_services:
            service_type = Service if 'href' in service else ServicePort
            decoded_ingress_services.append(service_type.from_json(service))
        self.ingress_services = decoded_ingress_services
        self.providers = [Actor.from_json(o) for o in self.providers] if self.providers else None
        self.consumers = [Actor.from_json(o) for o in self.consumers] if self.consumers else None


@dataclass
class LabelResolutionBlock(JsonObject):
    providers: List[str] = None
    consumers: List[str] = None


@dataclass
class Rule(BaseRule):
    enabled: bool = None
    resolve_labels_as: LabelResolutionBlock = None
    sec_connect: bool = None
    stateless: bool = None
    machine_auth: bool = None
    consuming_security_principals: List[Reference] = None
    unscoped_consumers: bool = None
    network_type: str = None

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.resolve_labels_as = LabelResolutionBlock.from_json(self.resolve_labels_as) if self.resolve_labels_as else None
        self.consuming_security_principals = [Reference.from_json(o) for o in self.consuming_security_principals] if self.consuming_security_principals else None
