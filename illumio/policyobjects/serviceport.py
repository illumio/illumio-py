from dataclasses import dataclass

from .jsonobject import JsonObject


@dataclass
class ServicePort(JsonObject):
    port: int
    proto: int
    to_port: int = None
    icmp_type: int = None
    icmp_code: int = None

    def _decode_complex_types(self) -> None:
        pass  # noop


@dataclass
class WindowsServicePort(ServicePort):
    service_name: str = None
    process_name: str = None
