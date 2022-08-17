# -*- coding: utf-8 -*-

"""This module provides common exception classes used throughout the application.

Copyright:
    © 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List

from .exceptions import IllumioException
from .util import (
    JsonObject,
    Reference,
    Error,
    ChangeType,
    EventStatus,
    EventSeverity,
    pce_api
)


@dataclass
class EventCreatedBy(JsonObject):
    @dataclass
    class _EventCreatedByAgent(Reference):
        hostname: str = None

    @dataclass
    class _EventCreatedByContainerCluster(Reference):
        name: str = None

    @dataclass
    class _EventCreatedByUser(Reference):
        username: str = None

    agent: _EventCreatedByAgent = None
    container_cluster: _EventCreatedByContainerCluster = None
    user: _EventCreatedByUser = None
    system: dict = None


@dataclass
class BaseEvent(Reference):
    event: str = None
    event_type: str = None
    uuid: str = None
    timestamp: str = None
    pce_fqdn: str = None
    severity: str = None
    status: str = None
    created_by: EventCreatedBy = None
    info: dict = None

    def _validate(self):
        if self.severity and not self.severity in EventSeverity:
            raise IllumioException("Invalid event severity: {}".format(self.severity))
        if self.status and not self.status in EventStatus:
            raise IllumioException("Invalid event status: {}".format(self.status))
        super()._validate()


@dataclass
class NotificationEvent(BaseEvent):
    notification_type: str = None


@dataclass
class ResourceEvent(BaseEvent):
    version: str = None
    org_id: int = None
    resource: dict = None
    changes: dict = None
    change_type: str = None

    def _validate(self):
        if self.change_type and not self.change_type in ChangeType:
            raise IllumioException("Invalid change_type: {}".format(self.change_type))
        super()._validate()


@dataclass
class ActionEvent(BaseEvent):
    task_name: str = None
    api_endpoint: str = None
    api_method: str = None
    http_status_code: int = None
    src_ip: str = None
    errors: List[Error] = None


@dataclass
@pce_api("events")
class Event(BaseEvent):
    """Represents an event object in the PCE.

    Events are read-only via the PCE API.

    See https://docs.illumio.com/core/21.5/Content/Guides/rest-api/pce-management/events.htm

    Usage:
        >>> pce.events.get(params={'max_results': 5, 'severity': EventSeverity.CRITICAL.value})
    """
    status: str = None
    action: ActionEvent = None
    resource_changes: List[ResourceEvent] = None
    notifications: List[NotificationEvent] = None


__all__ = [
    'Event',
    'NotificationEvent',
    'ResourceEvent',
    'ActionEvent',
]
