# -*- coding: utf-8 -*-

"""This module provides classes for traffic analysis using Explorer.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
import re
import socket
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Union, Optional

from illumio import IllumioException
from illumio.infrastructure import Network
from illumio.policyobjects import (
    IPList,
    Label,
    ServicePort,
    VirtualServer,
    VirtualService
)
from illumio.util import (
    JsonObject,
    Reference,
    Transmission,
    PolicyDecision,
    FlowDirection,
    TrafficState,
    FQDN_REGEX
)
from illumio.workloads import Workload

AND = 'and'
OR = 'or'


@dataclass
class TrafficQueryFilter(JsonObject):
    label: Reference = None
    workload: Reference = None
    ip_list: Reference = None
    ip_address: str = None
    fqdn: str = None
    transmission: str = None

    def _validate(self):
        if self.transmission and not self.transmission in Transmission:
            raise IllumioException("Invalid transmission: {}".format(self.transmission))


@dataclass
class TrafficQueryFilterBlock(JsonObject):
    # the include parameter is specified as a list of lists
    # of object references or key-value pairs
    include: List[List[TrafficQueryFilter]] = field(default_factory=list)
    exclude: List[TrafficQueryFilter] = field(default_factory=list)

    def __post_init__(self):
        self.include = _parse_traffic_filters(self.include, include=True)
        self.exclude = _parse_traffic_filters(self.exclude)
        super().__post_init__()


def _parse_traffic_filters(refs: List[Any], include=False) -> List[object]:
    traffic_objects = []
    for ref in refs:
        if type(ref) is not str:
            traffic_objects.append(ref)
            continue
        elif re.match(FQDN_REGEX, ref):
            if include:
                raise IllumioException("Cannot specify consumer FQDN filter")
            o = {'fqdn': ref}
        elif 'label' in ref:
            o = {'label': {'href': ref}}
        elif 'workload' in ref:
            o = {'workload': {'href': ref}}
        elif 'ip_list' in ref:
            o = {'ip_list': {'href': ref}}
        elif ref in Transmission:
            if include:
                raise IllumioException("Cannot specify consumer transmission filter")
            o = {'transmission': ref}
        else:
            try:
                socket.inet_aton(ref)  # check if the reference is an IP address
                o = {'ip_address': ref}
            except socket.error:
                raise IllumioException('Invalid traffic filter type: {}').format(ref)
        traffic_objects.append([o] if include else o)
    return traffic_objects


@dataclass
class TrafficQueryServiceBlock(JsonObject):
    include: List[ServicePort] = field(default_factory=list)
    exclude: List[ServicePort] = field(default_factory=list)

    def __post_init__(self):
        self.include = _parse_service_ports(self.include)
        self.exclude = _parse_service_ports(self.exclude)
        super().__post_init__()


def _parse_service_ports(service_ports: List[Union[ServicePort, dict]]):
    parsed_service_ports = []
    for service_port in service_ports:
        if type(service_port) is ServicePort:
            parsed_service_ports.append(service_port)
        elif type(service_port) is dict:
            parsed_service_ports.append(ServicePort.from_json(service_port))
        else:
            raise IllumioException("Invalid service port type: {}".format(type(service_port)))
    return parsed_service_ports


@dataclass
class TrafficQuery(JsonObject):
    start_date: Union[str, int, float]
    end_date: Union[str, int, float]
    sources: TrafficQueryFilterBlock = field(default_factory=TrafficQueryFilterBlock)
    destinations: TrafficQueryFilterBlock = field(default_factory=TrafficQueryFilterBlock)
    services: TrafficQueryServiceBlock = field(default_factory=TrafficQueryServiceBlock)
    policy_decisions: List[str] = field(default_factory=list)
    exclude_workloads_from_ip_list_query: bool = True
    sources_destinations_query_op: str = AND
    max_results: int = 100000
    query_name: str = None  # required for async traffic queries

    @staticmethod
    def build(start_date: Optional[Union[str, int, float]] = None,
            end_date: Optional[Union[str, int, float]] = None,
            include_sources=[], exclude_sources=[],
            include_destinations=[], exclude_destinations=[],
            include_services=[], exclude_services=[], policy_decisions=[],
            exclude_workloads_from_ip_list_query=True, max_results=100000,
            query_name=None) -> 'TrafficQuery':
        return TrafficQuery(
            start_date=start_date, end_date=end_date,
            sources=TrafficQueryFilterBlock(
                include=include_sources,
                exclude=exclude_sources
            ),
            destinations=TrafficQueryFilterBlock(
                include=include_destinations,
                exclude=exclude_destinations
            ),
            services=TrafficQueryServiceBlock(
                include=include_services,
                exclude=exclude_services
            ),
            policy_decisions=policy_decisions,
            exclude_workloads_from_ip_list_query=exclude_workloads_from_ip_list_query,
            max_results=max_results, query_name=query_name
        )

    def __post_init__(self):
        if type(self.start_date) is int or type(self.start_date) is float:
            self.start_date = self._convert_timestamp_to_date_string(self.start_date)
        if type(self.end_date) is int or type(self.end_date) is float:
            self.end_date = self._convert_timestamp_to_date_string(self.end_date)
        super().__post_init__()

    def _convert_timestamp_to_date_string(self, timestamp: Union[int, float]) -> str:
        try:
            # the Unix timestamp could be in seconds or milliseconds,
            # so check the number of digits; 12 digits in s is year 5138
            # and we could theoretically be looking at dates before 2001 (10 digits)
            if len(str(int(timestamp))) >= 12:
                timestamp = timestamp / 1000
            dt = datetime.utcfromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            raise IllumioException("Invalid start or end time provided for traffic analysis")

    def _validate(self):
        for policy_decision in self.policy_decisions:
            if not policy_decision in PolicyDecision:
                raise IllumioException("Invalid policy_decision: {}".format(policy_decision))
        if self.sources_destinations_query_op.lower() not in {AND, OR}:
            raise IllumioException("sources_destinations_query_op must be one of 'and' or 'or', was {}".format(self.sources_destinations_query_op))


@dataclass
class TrafficNode(JsonObject):
    ip: str = None
    label: Label = None
    workload: Workload = None
    ip_lists: List[IPList] = None
    virtual_server: VirtualServer = None
    virtual_service: VirtualService = None


@dataclass
class TimestampRange(JsonObject):
    first_detected: str
    last_detected: str


@dataclass
class TrafficFlow(JsonObject):
    src: TrafficNode
    dst: TrafficNode
    service: ServicePort = None
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
        if self.flow_direction and not self.flow_direction in FlowDirection:
            raise IllumioException("Invalid flow_direction: {}".format(self.flow_direction))
        if self.policy_decision and not self.policy_decision in PolicyDecision:
            raise IllumioException("Invalid policy_decision: {}".format(self.policy_decision))
        if self.state and not self.state in TrafficState:
            raise IllumioException("Invalid state: {}".format(self.state))
        if self.transmission and not self.transmission in Transmission:
            raise IllumioException("Invalid transmission: {}".format(self.transmission))
