from dataclasses import dataclass
from typing import List

from illumio.util import JsonObject, ModifiableObject


@dataclass
class ServicePort(JsonObject):
    port: int = None
    proto: int = None
    to_port: int = None
    icmp_type: int = None
    icmp_code: int = None
    service_name: str = None
    process_name: str = None
    windows_service_name: str = None
    user_name: str = None


@dataclass
class ServiceAddress(JsonObject):
    ip: str = None
    port: int = None
    proto: int = None
    fqdn: str = None
    description: str = None


@dataclass
class Service(ModifiableObject):
    service_ports: List[ServicePort] = None

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.service_ports = [ServicePort.from_json(o) for o in self.service_ports] if self.service_ports else None
