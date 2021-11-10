import json
from abc import ABC
from dataclasses import dataclass, asdict

from illumio import ignore_empty_keys


@dataclass
class JsonObject(ABC):

    def to_json(self) -> dict:
        return json.dumps(asdict(self, dict_factory=ignore_empty_keys))

    def _decode_complex_types(self) -> None:
        pass

    @classmethod
    def from_json(cls, data) -> 'JsonObject':
        data = json.loads(data) if type(data) is str else data
        o = cls(**data)
        o._decode_complex_types()
        return o


@dataclass
class PolicyObject(JsonObject):
    href: str = None
    name: str = None
    description: str = None
    created_at: str = None
    updated_at: str = None
    deleted_at: str = None
    update_type: str = None
