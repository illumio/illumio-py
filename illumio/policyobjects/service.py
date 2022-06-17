# -*- coding: utf-8 -*-

"""This module provides classes related to services and service ports.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from illumio.util import (
    JsonObject,
    MutableObject,
    pce_api,
    convert_protocol
)


@dataclass
class BaseService(JsonObject):
    port: int = None
    proto: int = None

    def __post_init__(self):
        if type(self.proto) is str:
            self.proto = convert_protocol(self.proto)
        super().__post_init__()


@dataclass
class ServicePort(BaseService):
    to_port: int = None
    icmp_type: int = None
    icmp_code: int = None
    service_name: str = None
    process_name: str = None
    windows_service_name: str = None
    user_name: str = None


@dataclass
@pce_api('services', is_sec_policy=True)
class Service(MutableObject):
    """Represents a service in the PCE.

    A service can be port-based or process-based (Windows services).

    Each service contains one or more objects defining the port, protocol, and/or
    process name used by an application running on a workload.

    Service objects are used to write rules or enforcement boundaries to allow
    or deny traffic on its defined ports and processes for workloads in the network.

    See https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/services.htm

    Usage:
        >>> from illumio import PolicyComputeEngine, Service, ServicePort
        >>> pce = PolicyComputeEngine('my.pce.com')
        >>> pce.set_credentials('api_key_username', 'api_key_secret')
        >>> service = Service(
        ...     name='S-HTTP',
        ...     service_ports=[
        ...         ServicePort(port=80, proto='tcp'),
        ...         ServicePort(port=443, proto='tcp')
        ...     ]
        ... )
        >>> service = pce.services.create(service)
        >>> service
        Service(
            href='/orgs/1/sec_policy/draft/services/15',
            name='S-HTTP',
            service_ports=[
                ServicePort(
                    port=80,
                    proto=6,
                    ...
                ),
                ...
            ],
            ...
        )
    """
    service_ports: List[ServicePort] = None
