from dataclasses import dataclass
from typing import List

from illumio import IllumioException
from illumio.infrastructure import ContainerCluster
from illumio.policyobjects import Label
from illumio.vulnerabilities import Vulnerability
from illumio.util import (
    JsonObject,
    Reference,
    ModifiableObject,
    LinkState,
    Mode,
    EnforcementMode,
    VisibilityLevel
)

from .ven import VEN, VENAgent


@dataclass
class Interface(JsonObject):
    name: str
    link_state: str = None
    address: str = None
    cidr_block: int = None
    default_gateway_address: str = None
    network: Reference = None
    network_detection_mode: str = None
    friendly_name: str = None
    loopback: str = None

    def _validate(self):
        if self.link_state and not LinkState.has_value(self.link_state.lower()):
            raise IllumioException("Invalid link_state: {}".format(self.link_state))

    def _decode_complex_types(self):
        self.network = Reference.from_json(self.network) if self.network else None


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
    created_at: int = None
    open_service_ports: List[WorkloadServicePort] = None

    def _decode_complex_types(self):
        self.open_service_ports = [WorkloadServicePort.from_json(o) for o in self.open_service_ports]


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

    def _decode_complex_types(self):
        if self.vulnerable_port_wide_exposure:
            self.vulnerable_port_wide_exposure = PortWideExposure.from_json(self.vulnerable_port_wide_exposure)


@dataclass
class DetectedVulnerability(JsonObject):
    ip_address: str = None
    port: int = None
    proto: int = None
    port_exposure: int = None
    port_wide_exposure: PortWideExposure = None
    workload: Reference = None
    vulnerability: Vulnerability = None
    vulnerability_report: Reference = None

    def _decode_complex_types(self):
        self.port_wide_exposure = PortWideExposure.from_json(self.port_wide_exposure) if self.port_wide_exposure else None
        self.workload = Reference.from_json(self.workload) if self.workload else None
        self.vulnerability = Vulnerability.from_json(self.vulnerability) if self.vulnerability else None
        self.vulnerability_report = Reference.from_json(self.vulnerability_report) if self.vulnerability_report else None


@dataclass
class IKEAuthenticationCertificate(JsonObject):
    pass


@dataclass
class Workload(ModifiableObject):
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
    caps: List[str] = None
    firewall_coexistence: str = None
    containers_inherit_host_policy: bool = None
    blocked_connection_action: str = None
    labels: List[Label] = None
    services: WorkloadServices = None
    vulnerabilities_summary: VulnerabilitiesSummary = None
    detected_vulnerabilities: List[DetectedVulnerability] = None
    agent: VENAgent = None
    ven: VEN = None
    mode: str = None
    enforcement_mode: str = None
    visibility_level: str = None
    selectively_enforced_services: List[Reference] = None
    container_cluster: ContainerCluster = None
    ike_authentication_certificate: IKEAuthenticationCertificate = None

    def _validate(self):
        if self.mode and not Mode.has_value(self.mode.lower()):
            raise IllumioException("Invalid mode: {}".format(self.mode))
        if self.enforcement_mode and not EnforcementMode.has_value(self.enforcement_mode.lower()):
            raise IllumioException("Invalid enforcement_mode: {}".format(self.enforcement_mode))
        if self.visibility_level and not VisibilityLevel.has_value(self.visibility_level.lower()):
            raise IllumioException("Invalid visibility_level: {}".format(self.visibility_level))

    def _decode_complex_types(self):
        super()._decode_complex_types()
        self.interfaces = [Interface.from_json(o) for o in self.interfaces] if self.interfaces else None
        self.labels = [Label.from_json(o) for o in self.labels] if self.labels else None
        self.services = WorkloadServices.from_json(self.services) if self.services else None
        self.vulnerabilities_summary = VulnerabilitiesSummary.from_json(self.vulnerabilities_summary) if self.vulnerabilities_summary else None
        self.detected_vulnerabilities = [DetectedVulnerability.from_json(o) for o in self.detected_vulnerabilities] if self.detected_vulnerabilities else None
        self.agent = VENAgent.from_json(self.agent) if self.agent else None
        self.ven = VEN.from_json(self.ven) if self.ven else None
        self.selectively_enforced_services = [Reference.from_json(o) for o in self.selectively_enforced_services] if self.selectively_enforced_services else None
        self.container_cluster = ContainerCluster.from_json(self.container_cluster) if self.container_cluster else None
        self.ike_authentication_certificate = IKEAuthenticationCertificate.from_json(self.ike_authentication_certificate) if self.ike_authentication_certificate else None
