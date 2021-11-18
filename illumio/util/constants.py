import re
from enum import Enum

ACTIVE = 'active'
DRAFT = 'draft'

ANY_IP_LIST_NAME = 'Any (0.0.0.0/0 and ::/0)'

FQDN_REGEX = re.compile('(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)')
HREF_REGEX = re.compile('^\/orgs\/\d+\/(?:sec_policy\/(?:active|draft)\/)?(?P<type>[a-zA-Z_]+)\/(?P<uid>[a-zA-Z0-9-]+)$')


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
