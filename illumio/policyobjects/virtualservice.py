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
from illumio.util import IllumioObject, Reference, MutableObject, pce_api

from .service import BaseService, ServicePort

HOST_ONLY = 'host_only'
INTERNAL_BRIDGE_NETWORK = 'internal_bridge_network'


@dataclass
class ServiceAddress(BaseService):
    """Defines a Service Address record for use in a Virtual Service address pool.

    A ServiceAddress can be defined with either an IP address or FQDN.

    If an IP is provided, one of a port number or network object HREF
    must be provided as well.

    If an FQDN is given it's sufficient by itself, but description or
    port values can optionally be provided.
    """
    ip: str = None
    fqdn: str = None
    network: Reference = None
    description: str = None


@dataclass
@pce_api('virtual_services', is_sec_policy=True)
class VirtualService(MutableObject):
    apply_to: str = None
    pce_fqdn: str = None
    service: Reference = None
    service_ports: List[ServicePort] = None
    service_addresses: List[ServiceAddress] = None
    ip_overrides: List[str] = None
    labels: List[Reference] = None

    def _validate(self):
        if self.apply_to and self.apply_to not in {HOST_ONLY, INTERNAL_BRIDGE_NETWORK}:
            raise IllumioException("Invalid 'apply_to' value: {}".format(self.apply_to))
        super()._validate()


@dataclass
class PortOverride(BaseService):
    to_port: int = None
    new_port: int = None
    new_to_port: int = None


@dataclass
@pce_api('service_bindings')
class ServiceBinding(IllumioObject):
    virtual_service: Reference = None
    workload: Reference = None
    port_overrides: List[PortOverride] = None
