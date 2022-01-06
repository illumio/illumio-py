import copy
import json
from abc import ABC
from dataclasses import dataclass, fields
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

    def to_json(self) -> Any:
        return deep_encode(self)

    @classmethod
    def from_json(cls, data) -> 'JsonObject':
        data = json.loads(data) if type(data) is str else data
        o = cls(**data)
        o._decode_complex_types()
        return o

    def _decode_complex_types(self) -> None:
        pass


def deep_encode(o: Any) -> Any:
    """
    Functionally similar to the dataclasses asdict function, but with the necessary
    adjustment of calling an optional custom encoding function for types that
    don't strictly mirror their dataclass field key-value pairs when json-encoded.
    """
    if issubclass(o.__class__, JsonObject):
        result = []
        if hasattr(o.__class__, '_encode'):
            return o._encode()
        for f in fields(o):
            value = deep_encode(getattr(o, f.name))
            result.append((f.name, value))
        return ignore_empty_keys(result)
    elif isinstance(o, (list, tuple)):
        return type(o)(deep_encode(v) for v in o)
    elif isinstance(o, dict):
        return type(o)((deep_encode(k), deep_encode(v)) for k, v in o.items())
    else:
        return copy.deepcopy(o)


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
        self.created_by = Reference.from_json(self.created_by) if self.created_by else None
        self.updated_by = Reference.from_json(self.updated_by) if self.updated_by else None
        self.deleted_by = Reference.from_json(self.deleted_by) if self.deleted_by else None
