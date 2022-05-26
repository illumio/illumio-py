# -*- coding: utf-8 -*-

"""This module provides classes related to Virtual Enfocement Node objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass, field
from typing import List

from illumio import IllumioException
from illumio.util import JsonObject, ModifiableObject, VisibilityLevel


@dataclass
class AgentConfig(JsonObject):
    mode: str = None
    log_traffic: bool = None
    security_policy_update_mode: str = None
    visibility_level: VisibilityLevel = None

    def _validate(self):
        if self.visibility_level and not self.visibility_level in VisibilityLevel:
            raise IllumioException("Invalid visibility_level: {}".format(self.visibility_level))


@dataclass
class SecureConnect(JsonObject):
    matching_issuer_name: str = None


@dataclass
class AgentHealthErrors(JsonObject):
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class AgentHealth(JsonObject):
    type: str = None
    severity: str = None
    audit_event: str = None


@dataclass
class AgentStatus(JsonObject):
    status: str = None
    uid: str = None
    instance_id: str = None
    last_heartbeat_on: str = None
    uptime_seconds: int = None
    agent_version: str = None
    managed_since: str = None
    fw_config_current: bool = None
    firewall_rule_count: int = None
    security_policy_refresh_at: str = None
    security_policy_applied_at: str = None
    security_policy_received_at: str = None
    agent_health_errors: AgentHealthErrors = None
    agent_health: List[AgentHealth] = None
    security_policy_sync_state: str = None


@dataclass
class VENAgent(ModifiableObject):
    config: AgentConfig = None
    secure_connect: SecureConnect = None
    status: AgentStatus = None
    unpair_allowed: bool = None
    active_pce_fqdn: str = None
    target_pce_fqdn: str = None
    type: str = None


@dataclass
class VEN(ModifiableObject):
    hostname: str = None
    name: str = None
    status: str = None
