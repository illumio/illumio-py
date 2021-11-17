import re
from dataclasses import dataclass
from enum import Enum
from typing import List

from .jsonutils import JsonObject

ANY_IP_LIST_NAME = 'Any (0.0.0.0/0 and ::/0)'

FQDN_REGEX = re.compile('(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)')
POLICY_OBJECT_HREF_REGEX = re.compile('^\/orgs\/\d+\/sec_policy\/(?:active|draft)\/(?P<type>[a-zA-Z_]+)\/(?P<uid>[a-zA-Z0-9-]+)$')


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


class IllumioEnum(Enum):

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class LinkState(IllumioEnum):
    UP = 'up'
    DOWN = 'down'
    UNKNOWN = 'unknown'


class Mode(IllumioEnum):
    IDLE = 'idle'
    ILLUMINATED = 'illuminated'
    ENFORCED = 'enforced'


class EnforcementMode(IllumioEnum):
    IDLE = 'idle'
    VISIBILITY_ONLY = 'visibility_only'
    FULL = 'full'
    SELECTIVE = 'selective'


class VisibilityLevel(IllumioEnum):
    FLOW_FULL_DETAIL = 'flow_full_detail'
    FLOW_SUMMARY = 'flow_summary'
    FLOW_DROPS = 'flow_drops'
    FLOW_OFF = 'flow_off'
    ENHANCED_DATA_COLLECTION = 'enhanced_data_collection'


class PolicyDecision(IllumioEnum):
    ALLOWED = 'allowed'
    BLOCKED = 'blocked'
    POTENTIALLY_BLOCKED = 'potentially_blocked'
    UNKNOWN = 'unknown'


class Transmission(IllumioEnum):
    BROADCAST = 'broadcast'
    MULTICAST = 'multicast'
    UNICAST = 'unicast'


class FlowDirection(IllumioEnum):
    INBOUND = 'inbound'
    OUTBOUND = 'outbound'


class TrafficState(IllumioEnum):
    ACTIVE = 'active'
    CLOSED = 'closed'
    TIMED_OUT = 'timed_out'
    SNAPSHOT = 'snapshot'
    NEW = 'new'
    UNKNOWN = 'unknown'
    INCOMPLETE = 'incomplete'
