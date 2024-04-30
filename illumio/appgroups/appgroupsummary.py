# -*- coding: utf-8 -*-

"""This module provides classes related to AppGroups and AppGroupSummarys.

Copyright:
    © 2024 Illumio

License:
    Apache2, see LICENSE for more details.

"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

from illumio.util import pce_api, JsonObject, ModeKeyTypes, VisibilityLevelKeyTypes


@dataclass
class AppGroup(JsonObject):
    """Represents an App Group in the PCE.
    App groups can contain labels in an Array representing the label hrefs that constitute the AppGroup
    """
    type: str = None
    href: str = None
    label_ids: List[int] = None
    num_workloads: int = None
    num_container_workloads: int = None
    num_virtual_services: int = None
    num_virtual_servers: int = None
    mode: List[int] = None
    container_workload_mode: List[int] = None
    visibility_level: List[int] = None
    caps: dict = None


@dataclass
class AppGroupLabelData(JsonObject):
    href: str = None
    key: str = None
    value: str = None


@dataclass
class AppGroupLabel(JsonObject):
    label: AppGroupLabelData = None


@dataclass
@pce_api('app_group_summary')
class AppGroupSummary(JsonObject):
    """Represents an App Group Summary in the PCE.
    App groups can contain labels in an Array representing the label hrefs that constitute the AppGroup
    """
    nodes: List[AppGroup] = None
    labels: Optional[Dict[str, AppGroupLabel]] = None
    mode_key: List[ModeKeyTypes] = None
    visibility_level_key: List[VisibilityLevelKeyTypes] = None
    signature: str = None
    updated_at: datetime = None
    version: int = None
    cached: bool = None


__all__ = [
    'AppGroupLabel',
    'AppGroupLabelData',
    'AppGroupSummary',
    'AppGroup'
]
