from dataclasses import dataclass, field
from typing import List

from illumio import IllumioException, IllumioEnum

from . import (
    JsonObject,
    IPList,
    Label,
    Network,
    Service,
    Workload,
    VirtualServer,
    VirtualService
)

AND = 'and'
OR = 'or'


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


@dataclass
class TrafficQueryFilter(JsonObject):
    label: Label = None
    workload: Workload = None
    ip_list: IPList = None
    ip_address: str = None
    fqdn: str = None
    transmission: str = None

    def _validate(self):
        if self.transmission and not Transmission.has_value(self.transmission):
            raise IllumioException("Invalid transmission: {}".format(self.transmission))

    def _decode_complex_types(self):
        self.label = Label(href=self.label['href']) if self.label else None
        self.workload = Workload(href=self.label['href']) if self.workload else None
        self.ip_list = IPList(href=self.label['href']) if self.ip_list else None


@dataclass
class TrafficQueryFilterBlock(JsonObject):
    # bafflingly, the include parameter is specified as a list of lists
    # of object references or key-value pairs.
    include: List[List[TrafficQueryFilter]] = field(default_factory=list)
    exclude: List[TrafficQueryFilter] = field(default_factory=list)

    def _decode_complex_types(self):
        self.include = [[TrafficQueryFilter.from_json(o) for o in block] for block in self.include]
        self.exclude = [TrafficQueryFilter.from_json(o) for o in self.exclude]


@dataclass
class TrafficQueryServiceBlock(JsonObject):
    include: List[Service] = field(default_factory=list)
    exclude: List[Service] = field(default_factory=list)

    def _decode_complex_types(self):
        self.include = [Service.from_json(o) for o in self.include]
        self.exclude = [Service.from_json(o) for o in self.exclude]


@dataclass
class TrafficQuery(JsonObject):
    start_date: str
    end_date: str
    sources: TrafficQueryFilterBlock = field(default_factory=TrafficQueryFilterBlock)
    destinations: TrafficQueryFilterBlock = field(default_factory=TrafficQueryFilterBlock)
    services: TrafficQueryServiceBlock = field(default_factory=TrafficQueryServiceBlock)
    policy_decisions: List[str] = field(default_factory=list)
    exclude_workloads_from_ip_list_query: bool = True
    sources_destinations_query_op: str = AND
    max_results: int = 100000
    query_name: str = None  # required for async traffic queries

    def _validate(self):
        for policy_decision in self.policy_decisions:
            if not PolicyDecision.has_value(policy_decision):
                raise IllumioException("Invalid policy_decision: {}".format(policy_decision))

    def _decode_complex_types(self):
        self.sources = TrafficQueryFilterBlock.from_json(self.sources)
        self.destinations = TrafficQueryFilterBlock.from_json(self.destinations)
        self.services = TrafficQueryServiceBlock.from_json(self.services)


@dataclass
class TrafficNode(JsonObject):
    ip: str = None
    label: Label = None
    workload: Workload = None
    ip_lists: List[IPList] = None
    virtual_server: VirtualServer = None
    virtual_service: VirtualService = None

    def _decode_complex_types(self):
        self.label = Label.from_json(self.label) if self.label else None
        self.workload = Workload.from_json(self.workload) if self.workload else None
        self.ip_lists = [IPList.from_json(o) for o in self.ip_lists] if self.ip_lists else None
        self.virtual_server = VirtualServer.from_json(self.virtual_server) if self.virtual_server else None
        self.virtual_service = VirtualService.from_json(self.virtual_service) if self.virtual_service else None


@dataclass
class TimestampRange(JsonObject):
    first_detected: str
    last_detected: str


@dataclass
class TrafficFlow(JsonObject):
    src: TrafficNode
    dst: TrafficNode
    service: Service = None
    num_connections: int = None
    state: str = None
    timestamp_range: TimestampRange = None
    dst_bi: int = None
    dst_bo: int = None
    policy_decision: str = None
    flow_direction: str = None
    transmission: str = None
    icmp_type: int = None
    icmp_code: int = None
    network: Network = None

    def _validate(self):
        if self.flow_direction and not FlowDirection.has_value(self.flow_direction):
            raise IllumioException("Invalid flow_direction: {}".format(self.flow_direction))
        if self.policy_decision and not PolicyDecision.has_value(self.policy_decision):
            raise IllumioException("Invalid policy_decision: {}".format(self.policy_decision))
        if self.transmission and not Transmission.has_value(self.transmission):
            raise IllumioException("Invalid transmission: {}".format(self.transmission))

    def _decode_complex_types(self):
        self.src = TrafficNode.from_json(self.src)
        self.dst = TrafficNode.from_json(self.dst)
        self.timestamp_range = TimestampRange.from_json(self.timestamp_range) if self.timestamp_range else None
        self.service = Service.from_json(self.service) if self.service else None
