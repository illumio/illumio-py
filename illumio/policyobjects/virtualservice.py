from dataclasses import dataclass
from typing import List

from .user import UserObject
from .label import Label
from .service import ServiceAddress, Service

from illumio import IllumioException

HOST_ONLY = 'host_only'
INTERNAL_BRIDGE_NETWORK = 'internal_bridge_network'


@dataclass
class VirtualService(UserObject):
    apply_to: str = HOST_ONLY
    pce_fqdn: str = None
    service_addresses: List[ServiceAddress] = None
    service_ports: List[Service] = None
    ip_overrides: List[str] = None
    labels: List[Label] = None
    caps: List[str] = None

    def __post_init__(self):
        if not self.name:
            raise IllumioException("No name specified for Virtual Service")
        if self.apply_to not in {HOST_ONLY, INTERNAL_BRIDGE_NETWORK}:
            raise IllumioException("Invalid 'apply_to' value: {}".format(self.apply_to))

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.service_ports = [Service.from_json(o) for o in self.service_ports]
        self.service_addresses = [ServiceAddress.from_json(o) for o in self.service_addresses]
        self.labels = [Label.from_json(o) for o in self.labels]
