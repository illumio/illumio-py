from dataclasses import dataclass
from enum import Enum

from .functions import *
from .jsonutils import *


@dataclass
class IllumioObject(JsonObject):
    href: str = None
    name: str = None
    description: str = None
    created_at: str = None
    updated_at: str = None
    deleted_at: str = None
    update_type: str = None
    delete_type: str = None


class IllumioEnum(Enum):

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
