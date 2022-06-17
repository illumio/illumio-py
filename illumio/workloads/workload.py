# -*- coding: utf-8 -*-

"""This module provides classes related to workload objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List, Union

from illumio import IllumioException
from illumio.infrastructure import ContainerCluster
from illumio.policyobjects import Label, BaseService, Service, ServicePort
from illumio.vulnerabilities import Vulnerability
from illumio.util import (
    JsonObject,
    Reference,
    MutableObject,
    LinkState,
    EnforcementMode,
    VisibilityLevel,
    pce_api
)

from .ven import VEN, VENAgent


@dataclass
class Interface(JsonObject):
    name: str = None
    link_state: str = None
    address: str = None
    cidr_block: int = None
    default_gateway_address: str = None
    network: Reference = None
    network_detection_mode: str = None
    friendly_name: str = None
    loopback: bool = None

    def _validate(self):
        if self.link_state and not self.link_state in LinkState:
            raise IllumioException("Invalid link_state: {}".format(self.link_state))
        super()._validate()


@dataclass
class WorkloadServicePort(JsonObject):
    port: int = None
    protocol: int = None
    address: str = None
    user: str = None
    package: str = None
    process_name: str = None
    win_service_name: str = None


@dataclass
class WorkloadServices(JsonObject):
    uptime_seconds: int = None
    open_service_ports: List[WorkloadServicePort] = None


@dataclass
class PortWideExposure(JsonObject):
    any: bool = None
    ip_list: bool = None


@dataclass
class VulnerabilitiesSummary(JsonObject):
    num_vulnerabilities: int = None
    vulnerable_port_exposure: int = None
    vulnerable_port_wide_exposure: PortWideExposure = None
    vulnerability_exposure_score: int = None
    vulnerability_score: int = None
    max_vulnerability_score: int = None


@dataclass
class DetectedVulnerability(BaseService):
    ip_address: str = None
    port_exposure: int = None
    port_wide_exposure: PortWideExposure = None
    workload: Reference = None
    vulnerability: Vulnerability = None
    vulnerability_report: Reference = None


@dataclass
class IKEAuthenticationCertificate(JsonObject):
    pass


@dataclass
@pce_api('workloads')
class Workload(MutableObject):
    """Represents a workload in the PCE.

    See https://docs.illumio.com/core/21.5/Content/Guides/security-policy/workloads/_ch-workloads.htm

    Usage:
        >>> from illumio import PolicyComputeEngine, Workload, Interface, EnforcementMode
        >>> pce = PolicyComputeEngine('my.pce.com')
        >>> pce.set_credentials('api_key_username', 'api_key_secret')
        >>> role_label = pce.labels.create({'key': 'role', 'value': 'Web'})
        >>> app_label = pce.labels.create({'key': 'app', 'value': 'App'})
        >>> env_label = pce.labels.create({'key': 'env', 'value': 'Development'})
        >>> loc_label = pce.labels.create({'key': 'loc', 'value': 'NYC-Datacenter'})
        >>> workload = Workload(
        ...     name='Web 01',
        ...     hostname='web01.lab.company.com',
        ...     public_ip='10.8.17.229',
        ...     labels=[role_label, app_label, env_label, loc_label],
        ...     interfaces=[
        ...         Interface(
        ...             name='lo0',
        ...             address='127.0.0.1',
        ...             link_state='up'
        ...         )
        ...     ],
        ...     enforcement_mode=EnforcementMode.SELECTIVE,
        ...     online=True
        ... )
        >>> workload = pce.workloads.create(workload)
        >>> workload
        Workload(
            href='/orgs/1/workloads/572eb23e-a891-42b5-b488-cd9ffe3622f5',
            name='Web 01',
            hostname='web01.lab.company.com',
            public_ip='10.8.17.229',
            labels=[
                Label(key='role', value='Web', ...),
                ...
            ],
            interfaces=[
                Interface(
                    name='lo0',
                    address='127.0.0.1',
                    link_state='up'
                )
            ],
            enforcement_mode='selective',
            online=True,
            ...
        )
    """
    hostname: str = None
    os_type: str = None
    service_principal_name: str = None
    agent_to_pce_certificate_authentication_id: str = None
    distinguished_name: str = None
    public_ip: str = None
    interfaces: List[Interface] = None
    service_provider: str = None
    data_center: str = None
    data_center_zone: str = None
    os_id: str = None
    os_detail: str = None
    online: bool = None
    deleted: bool = None
    ignored_interface_names: List[str] = None
    firewall_coexistence: str = None
    containers_inherit_host_policy: bool = None
    blocked_connection_action: str = None
    labels: List[Reference] = None
    services: WorkloadServices = None
    vulnerabilities_summary: VulnerabilitiesSummary = None
    detected_vulnerabilities: List[DetectedVulnerability] = None
    agent: VENAgent = None
    ven: VEN = None
    enforcement_mode: str = None
    visibility_level: str = None
    num_enforcement_boundaries: int = None
    selectively_enforced_services: List[Union[Service, ServicePort]] = None
    container_cluster: ContainerCluster = None
    ike_authentication_certificate: IKEAuthenticationCertificate = None

    def _validate(self):
        if self.enforcement_mode and not self.enforcement_mode in EnforcementMode:
            raise IllumioException("Invalid enforcement_mode: {}".format(self.enforcement_mode))
        if self.visibility_level and not self.visibility_level in VisibilityLevel:
            raise IllumioException("Invalid visibility_level: {}".format(self.visibility_level))
        super()._validate()

    def _decode_complex_types(self):
        enforced_services = []
        for service in self.selectively_enforced_services or []:
            service_type = Service if 'href' in service else ServicePort
            enforced_services.append(service_type.from_json(service))
        self.selectively_enforced_services = enforced_services if enforced_services else None
        super()._decode_complex_types()
