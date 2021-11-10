from dataclasses import dataclass

from .policyobject import JsonObject


@dataclass
class Service(JsonObject):
    port: int = None
    proto: int = None
    to_port: int = None
    icmp_type: int = None
    icmp_code: int = None
    service_name: str = None
    process_name: str = None
    windows_service_name: str = None
    user_name: str = None
    # additional custom fields from Workload services definition. baffling
    address: str = None
    package: str = None
    win_service_name: str = None


@dataclass
class ServiceAddress(JsonObject):
    ip: str = None
    port: int = None
    proto: int = None
    fqdn: str = None
    description: str = None
