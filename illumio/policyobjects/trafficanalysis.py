from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from illumio import IllumioException

from .policyobject import JsonObject
from .iplist import IPList
from .label import Label
from .service import Service
from .workload import Workload

ALLOWED = 'allowed'
BLOCKED = 'blocked'
POTENTIALLY_BLOCKED = 'potentially_blocked'
UNKNOWN = 'unknown'

BROADCAST = 'broadcast'
MULTICAST = 'multicast'
UNICAST = 'unicast'

AND = 'and'
OR = 'or'


@dataclass
class TrafficQueryFilter(JsonObject):
    label: Label = None
    workload: Workload = None
    ip_list: IPList = None
    ip_address: str = None
    fqdn: str = None
    transmission: str = None

    def __post_init__(self):
        if self.transmission and self.transmission not in {BROADCAST, MULTICAST, UNICAST}:
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

    def __post_init__(self):
        self._validate_start_end_dates()
        self._validate_policy_decisions()

    def _decode_complex_types(self):
        self.sources = TrafficQueryFilterBlock.from_json(self.sources)
        self.destinations = TrafficQueryFilterBlock.from_json(self.destinations)
        self.services = TrafficQueryServiceBlock.from_json(self.services)

    def _validate_start_end_dates(self):
        try:
            start_date = datetime.strptime(self.start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            raise IllumioException("Invalid start/end dates: must be valid ISO-8601 format") from e
        if start_date >= datetime.now():
            raise IllumioException("Invalid date range: start date {} occurs after current time".format(self.start_date))
        if start_date >= end_date:
            raise IllumioException("Invalid date range: start date {} occurs after end date {}".format(self.start_date, self.end_date))

    def _validate_policy_decisions(self):
        for policy_decision in self.policy_decisions:
            if policy_decision not in {ALLOWED, BLOCKED, POTENTIALLY_BLOCKED, UNKNOWN}:
                raise IllumioException("Invalid policy_decision: {}".format(policy_decision))


@dataclass
class TrafficFlow(JsonObject):
    pass
