from dataclasses import dataclass, field
from typing import List

from illumio import IllumioException, JsonObject, UserObject
from illumio.util import VisibilityLevel


@dataclass
class AgentConfig(JsonObject):
    mode: str = None
    log_traffic: bool = None
    security_policy_update_mode: str = None
    visibility_level: VisibilityLevel = None

    def _validate(self):
        if self.visibility_level and not VisibilityLevel.has_value(self.visibility_level.lower()):
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

    def _decode_complex_types(self) -> None:
        if self.agent_health_errors:
            self.agent_health_errors = AgentHealthErrors.from_json(self.agent_health_errors)
        self.agent_health = [AgentHealth.from_json(o) for o in self.agent_health] if self.agent_health else None


@dataclass
class VENAgent(UserObject):
    config: AgentConfig = None
    secure_connect: SecureConnect = None
    status: AgentStatus = None
    unpair_allowed: bool = None
    active_pce_fqdn: str = None
    target_pce_fqdn: str = None
    type: str = None

    def _decode_complex_types(self):
        self.config = AgentConfig.from_json(self.config) if self.config else None
        self.secure_connect = SecureConnect.from_json(self.secure_connect) if self.secure_connect else None
        self.status = AgentStatus.from_json(self.status) if self.status else None


@dataclass
class VEN(UserObject):
    hostname: str = None
    name: str = None
    status: str = None
