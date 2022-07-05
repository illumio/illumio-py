# -*- coding: utf-8 -*-

"""This module provides classes related to pairing profile objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass, fields
from typing import List, Union

from illumio import IllumioException
from illumio.util import (
    Reference,
    MutableObject,
    EnforcementMode,
    VisibilityLevel,
    pce_api,
    ignore_empty_keys,
    flatten_ref
)


@dataclass
@pce_api('pairing_profiles')
class PairingProfile(MutableObject):
    """Represents a pairing profile in the PCE.

    Pairing profiles are used to configure VEN defaults and generate keys
    for VEN pairing  on workloads that will be managed by the PCE.

    Usage:
        >>> from illumio.workloads import PairingProfile
        >>> pairing_profile = PairingProfile(
        ...     name='PP-DATABASE-VENS',
        ...     enabled=True,
        ...     enforcement_mode='visibility_only',
        ...     visibility_level='flows_summary'
        ... )
        >>> pairing_profile = pce.create_pairing_profile(pairing_profile)
        >>> pairing_profile
        PairingProfile(
            href='/orgs/1/pairing_profiles/19',
            name='PP-DATABASE-VENS',
            enabled=True,
            enforcement_mode='visibility_only',
            visibility_level='flows_summary',
            ...
        )
    """
    enabled: bool = None
    agent_software_release: str = None
    enforcement_mode: str = None
    enforcement_mode_lock: bool = None
    visibility_level: str = None
    visibility_level_lock: bool = None
    allowed_uses_per_key: Union[str, int] = None
    key_lifespan: Union[str, int] = None

    labels: List[Reference] = None
    role_label_lock: bool = None
    app_label_lock: bool = None
    env_label_lock: bool = None
    loc_label_lock: bool = None

    total_use_count: int = None
    is_default: bool = None
    last_pairing_at: str = None

    def _validate(self):
        if self.enforcement_mode and not self.enforcement_mode in EnforcementMode:
            raise IllumioException("Invalid enforcement_mode: {}".format(self.enforcement_mode))
        if self.visibility_level and not self.visibility_level in VisibilityLevel:
            raise IllumioException("Invalid visibility_level: {}".format(self.visibility_level))
        super()._validate()

    def _encode(self):
        """Defines custom encoding rules for pairing profiles.

        The allowed_uses_per_key and key_lifespan parameters have strict schema
        contraints in the PCE - values must either be 'unlimited' or an integer
        which we enforce here. Other fields use the default encoding method and
        labels is flattened to just include HREFs.
        """
        result = []
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name in ['allowed_uses_per_key', 'key_lifespan']:
                if isinstance(value, str) and value != 'unlimited':
                    if not value.isnumeric():
                        raise IllumioException("Invalid '{}' value: must be 'unlimited' or int".format(f.name))
                    value = int(value)
            if f.name == 'labels':
                value = flatten_ref(f.type, value)
            result.append((f.name, value))
        return ignore_empty_keys(result)
