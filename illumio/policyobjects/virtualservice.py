# -*- coding: utf-8 -*-

"""This module provides classes related to virtual services.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from illumio import IllumioException
from illumio.util import IllumioObject, Reference, ModifiableObject
from illumio.workloads import Workload

from .label import Label
from .service import BaseService, ServiceAddress, ServicePort

HOST_ONLY = 'host_only'
INTERNAL_BRIDGE_NETWORK = 'internal_bridge_network'


@dataclass
class VirtualService(ModifiableObject):
    apply_to: str = None
    pce_fqdn: str = None
    service_addresses: List[ServiceAddress] = None
    service_ports: List[ServicePort] = None
    ip_overrides: List[str] = None
    labels: List[Label] = None

    def _validate(self):
        if self.apply_to and self.apply_to not in {HOST_ONLY, INTERNAL_BRIDGE_NETWORK}:
            raise IllumioException("Invalid 'apply_to' value: {}".format(self.apply_to))


@dataclass
class PortOverride(BaseService):
    to_port: int = None
    new_port: int = None
    new_to_port: int = None


@dataclass
class ServiceBinding(IllumioObject):
    virtual_service: Reference = None
    workload: Workload = None
    port_overrides: List[PortOverride] = None
