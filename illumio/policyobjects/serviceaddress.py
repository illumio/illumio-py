from dataclasses import dataclass

from .jsonobject import JsonObject


@dataclass
class ServiceAddress(JsonObject):
    ip: str = None
    port: int = None
    proto: int = None
    fqdn: str = None
    description: str = None

    def _decode_complex_types(self) -> None:
        pass  # noop
