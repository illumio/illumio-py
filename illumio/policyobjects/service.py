from dataclasses import dataclass

from illumio import JsonObject

from illumio.accessmanagement import UserObject


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
    # additional custom fields from Workload services definition
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


@dataclass
class Service(UserObject):
    pass
