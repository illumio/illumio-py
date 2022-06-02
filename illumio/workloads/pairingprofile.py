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
from illumio.util import (
    Reference,
    ModifiableObject,
    EnforcementMode,
    VisibilityLevel,
    pce_api
)


@dataclass
@pce_api('pairing_profiles')
class PairingProfile(ModifiableObject):
    # the enabled flag is required when creating
    # pairing profiles, so set it to default to True
    enabled: bool = True
    agent_software_release: str = None
    enforcement_mode: str = None
    enforcement_mode_lock: bool = True
    visibility_level: str = None
    visibility_level_lock: bool = True
    allowed_uses_per_key: Union[str, int] = 'unlimited'
    key_lifespan: Union[str, int] = 'unlimited'

    labels: List[Reference] = None
    role_label_lock: bool = True
    app_label_lock: bool = True
    env_label_lock: bool = True
    loc_label_lock: bool = True

    total_use_count: int = None
    is_default: bool = None
    last_pairing_at: str = None

    def _validate(self):
        if self.enforcement_mode and not self.enforcement_mode in EnforcementMode:
            raise IllumioException("Invalid enforcement_mode: {}".format(self.enforcement_mode))
        if self.visibility_level and not self.visibility_level in VisibilityLevel:
            raise IllumioException("Invalid visibility_level: {}".format(self.visibility_level))
        super()._validate()
