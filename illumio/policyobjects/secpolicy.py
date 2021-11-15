from dataclasses import dataclass, field
from typing import List

from . import (
    LabelGroup,
    LabelSet,
    Service,
    IPList,
    VirtualService,
    VirtualServer
)

from illumio import JsonObject, IllumioException
from illumio.accessmanagement import UserObject
from illumio.rules import Ruleset, EnforcementBoundary
from illumio.infrastructure import SecureConnectGateway


@dataclass
class FirewallSetting(UserObject):
    allow_dhcp_client: bool = None
    log_dropped_multicast: bool = None
    log_dropped_broadcast: bool = None
    allow_traceroute: bool = None
    allow_ipv6: bool = None
    ipv6_mode: str = None
    network_detection_mode: str = None
    ike_authentication_type: str = None
    static_policy_scopes: List[LabelSet] = None
    firewall_coexistence: List[LabelSet] = None
    containers_inherit_host_policy_scopes: List[LabelSet] = None
    blocked_connection_reject_scopes: List[LabelSet] = None
    loopback_interfaces_in_policy_scopes: List[LabelSet] = None


@dataclass
class PolicyChangeset(JsonObject):
    label_groups: List[LabelGroup] = field(default_factory=list)
    services: List[Service] = field(default_factory=list)
    rule_sets: List[Ruleset] = field(default_factory=list)
    ip_lists: List[IPList] = field(default_factory=list)
    virtual_services: List[VirtualService] = field(default_factory=list)
    firewall_settings: List[FirewallSetting] = field(default_factory=list)
    enforcement_boundaries: List[EnforcementBoundary] = field(default_factory=list)
    secure_connect_gateways: List[SecureConnectGateway] = field(default_factory=list)
    virtual_servers: List[VirtualServer] = field(default_factory=list)

    @staticmethod
    def build(hrefs: List[str]):
        changeset = PolicyChangeset()
        for href in hrefs:
            if 'label_group' in href:
                changeset.label_groups.append(LabelGroup(href=href))
            elif 'rule_sets' in href:
                changeset.rule_sets.append(Ruleset(href=href))
            elif 'ip_lists' in href:
                changeset.ip_lists.append(IPList(href=href))
            elif 'virtual_services' in href:
                changeset.virtual_services.append(VirtualService(href=href))
            elif 'services' in href:
                changeset.services.append(Service(href=href))
            elif 'firewall_settings' in href:
                changeset.firewall_settings.append(FirewallSetting(href=href))
            elif 'enforcement_boundaries' in href:
                changeset.enforcement_boundaries.append(EnforcementBoundary(href=href))
            elif 'secure_connect_gateways' in href:
                changeset.secure_connect_gateways.append(SecureConnectGateway(href=href))
            elif 'virtual_servers' in href:
                changeset.virtual_servers.append(VirtualServer(href=href))
            else:
                raise IllumioException('Invalid HREF in policy provision changeset: {}'.format(href))
        return changeset
