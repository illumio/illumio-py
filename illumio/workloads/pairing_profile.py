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
    ModifiableObject,
    LinkState,
    Mode,
    EnforcementMode,
    VisibilityLevel
)


@dataclass
class PairingProfile(ModifiableObject):
    # the enabled flag is required when creating
    # pairing profiles, so set it to default to True
    enabled: bool = True
    agent_software_release: str = None
    enforcement_mode: str = None
    enforcement_mode_lock: bool = None
    visibility_level: str = None
    visibility_level_lock: bool = None
    allowed_uses_per_key: str = None
    key_lifespan: str = None

    labels: List[Reference] = None
    role_label_lock: bool = None
    app_label_lock: bool = None
    env_label_lock: bool = None
    loc_label_lock: bool = None

    total_use_count: int = None
    is_default: bool = None
    last_pairing_at: str = None

    # Deprecated parameters
    mode: str = None
    mode_lock: bool = None
    log_traffic: bool = None
    log_traffic_lock: bool = None

    def _validate(self):
        if self.mode and not self.mode in Mode:
            raise IllumioException("Invalid mode: {}".format(self.mode))
        if self.enforcement_mode and not self.enforcement_mode in EnforcementMode:
            raise IllumioException("Invalid enforcement_mode: {}".format(self.enforcement_mode))
        if self.visibility_level and not self.visibility_level in VisibilityLevel:
            raise IllumioException("Invalid visibility_level: {}".format(self.visibility_level))
