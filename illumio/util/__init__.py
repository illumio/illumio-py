from enum import Enum

from .functions import *
from .jsonutils import *


class IllumioEnum(Enum):

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
