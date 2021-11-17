from dataclasses import dataclass
from typing import List

from illumio import IllumioException
from illumio.util import IllumioObject, Reference, JsonObject, ModifiableObject

from .label import Label
from .service import ServiceAddress, ServicePort

HOST_ONLY = 'host_only'
INTERNAL_BRIDGE_NETWORK = 'internal_bridge_network'


@dataclass
class VirtualService(ModifiableObject):
    apply_to: str = None
    pce_fqdn: str = None
    service_addresses: List[ServiceAddress] = None
    service_ports: List[ServicePort] = None
    ip_overrides: List[str] = None
    labels: List[Label] = None

    def _validate(self):
        if self.apply_to and self.apply_to not in {HOST_ONLY, INTERNAL_BRIDGE_NETWORK}:
            raise IllumioException("Invalid 'apply_to' value: {}".format(self.apply_to))

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.service_ports = [ServicePort.from_json(o) for o in self.service_ports] if self.service_ports else None
        self.service_addresses = [ServiceAddress.from_json(o) for o in self.service_addresses] if self.service_addresses else None
        self.labels = [Label.from_json(o) for o in self.labels] if self.labels else None


@dataclass
class PortOverride(JsonObject):
    port: int = None
    to_port: int = None
    proto: int = None
    new_port: int = None
    new_to_port: int = None


@dataclass
class ServiceBinding(IllumioObject):
    virtual_service: Reference = None
    workload: Reference = None
    port_overrides: List[PortOverride] = None

    def _decode_complex_types(self):
        self.virtual_service = Reference.from_json(self.virtual_service) if self.virtual_service else None
        self.workload = Reference.from_json(self.workload) if self.workload else None
        self.port_overrides = [PortOverride.from_json(o) for o in self.port_overrides] if self.port_overrides else None
