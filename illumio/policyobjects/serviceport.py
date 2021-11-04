from dataclasses import asdict, dataclass

from .policyobject import PolicyObject

from illumio import ignore_empty_keys


@dataclass
class ServicePort(PolicyObject):
    port: int
    proto: int
    to_port: int = None
    icmp_type: int = None
    icmp_code: int = None

    def to_json(self) -> dict:
        return asdict(self, dict_factory=ignore_empty_keys)
