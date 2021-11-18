import json
from abc import ABC
from dataclasses import dataclass, asdict
from typing import List, Any

from .functions import ignore_empty_keys

_default = json.JSONEncoder()  # fall back to the default encoder for non-Illumio API objects


class IllumioEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return getattr(o.__class__, "to_json", _default.default)(o)


@dataclass
class JsonObject(ABC):

    def __post_init__(self):
        self._validate()

    def _validate(self):
        pass

    def to_json(self) -> dict:
        return asdict(self, dict_factory=ignore_empty_keys)

    def _decode_complex_types(self) -> None:
        pass

    @classmethod
    def from_json(cls, data) -> 'JsonObject':
        data = json.loads(data) if type(data) is str else data
        o = cls(**data)
        o._decode_complex_types()
        return o


@dataclass
class Reference(JsonObject):
    href: str = None


@dataclass
class IllumioObject(JsonObject):
    href: str = None
    name: str = None
    description: str = None
    external_data_set: str = None
    external_data_reference: str = None


@dataclass
class ModifiableObject(IllumioObject):
    created_at: str = None
    updated_at: str = None
    deleted_at: str = None
    update_type: str = None
    delete_type: str = None
    created_by: Reference = None
    updated_by: Reference = None
    deleted_by: Reference = None
    caps: List[str] = None

    def _decode_complex_types(self) -> None:
        self.created_by = Reference(href=self.created_by) if self.created_by else None
        self.updated_by = Reference(href=self.updated_by) if self.updated_by else None
        self.deleted_by = Reference(href=self.deleted_by) if self.deleted_by else None
