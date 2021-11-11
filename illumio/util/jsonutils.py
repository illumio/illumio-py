import json
from abc import ABC
from dataclasses import dataclass, asdict
from typing import Any

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
