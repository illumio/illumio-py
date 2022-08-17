# -*- coding: utf-8 -*-

"""Stub for PCE interface function definitions"""
from typing import Any, List, overload

from requests import Response

from illumio import (
    IllumioObject,
    Reference,
    IPList,
    TrafficQuery,
    TrafficFlow,
    PolicyVersion
)


class PolicyComputeEngine:
    base_url: str
    org_id: str

    def __init__(self, url: str, port: str, version: str, org_id: str) -> None: ...

    def _setup_retry(self): ...

    def set_credentials(self, username: str, password: str) -> None: ...

    def set_proxies(self, http_proxy: str, https_proxy: str) -> None: ...

    def _request(self, method: str, endpoint: str, include_org: bool, **kwargs) -> Response: ...

    def _build_url(self, endpoint: str, include_org: bool): ...

    def _encode_body(self, kwargs): ...

    def _get_error_message_from_response(self, response: Response) -> str: ...

    def get(self, endpoint: str, **kwargs) -> Response: ...

    def post(self, endpoint: str, **kwargs) -> Response: ...

    def put(self, endpoint: str, **kwargs) -> Response: ...

    def delete(self, endpoint: str, **kwargs) -> Response: ...

    def get_collection(self, endpoint: str, **kwargs) -> Response: ...

    @overload
    def _async_poll(self, job_location: str, retry_time: int) -> str: ...
    @overload
    def _async_poll(self, job_location: str, retry_time: float) -> str: ...

    def check_connection(self, **kwargs) -> bool: ...

    class _PCEObjectAPI:
        def __init__(self, pce: 'PolicyComputeEngine', api_data: object) -> None: ...

        def _build_endpoint(self, policy_version: str, parent: Any) -> str: ...

        @overload
        def get_by_reference(self, reference: str, **kwargs) -> IllumioObject: ...
        @overload
        def get_by_reference(self, reference: Reference, **kwargs) -> IllumioObject: ...
        @overload
        def get_by_reference(self, reference: dict, **kwargs) -> IllumioObject: ...

        @overload
        def get(self, policy_version: str, parent: str, **kwargs) -> List[IllumioObject]: ...
        @overload
        def get(self, policy_version: str, parent: Reference, **kwargs) -> List[IllumioObject]: ...
        @overload
        def get(self, policy_version: str, parent: dict, **kwargs) -> List[IllumioObject]: ...

        @overload
        def get_all(self, policy_version: str, parent: str, **kwargs) -> List[IllumioObject]: ...
        @overload
        def get_all(self, policy_version: str, parent: Reference, **kwargs) -> List[IllumioObject]: ...
        @overload
        def get_all(self, policy_version: str, parent: dict, **kwargs) -> List[IllumioObject]: ...

        @overload
        def get_async(self, policy_version: str, parent: str, **kwargs) -> List[IllumioObject]: ...
        @overload
        def get_async(self, policy_version: str, parent: Reference, **kwargs) -> List[IllumioObject]: ...
        @overload
        def get_async(self, policy_version: str, parent: dict, **kwargs) -> List[IllumioObject]: ...

        @overload
        def create(self, body: Any, parent: str, **kwargs) -> IllumioObject: ...
        @overload
        def create(self, body: Any, parent: Reference, **kwargs) -> IllumioObject: ...
        @overload
        def create(self, body: Any, parent: dict, **kwargs) -> IllumioObject: ...

        @overload
        def update(self, reference: str, body: Any, **kwargs) -> None: ...
        @overload
        def update(self, reference: Reference, body: Any, **kwargs) -> None: ...
        @overload
        def update(self, reference: dict, body: Any, **kwargs) -> None: ...

        @overload
        def delete(self, reference: str, **kwargs) -> None: ...
        @overload
        def delete(self, reference: Reference, **kwargs) -> None: ...
        @overload
        def delete(self, reference: dict, **kwargs) -> None: ...

        def bulk_create(self, objects_to_create: List[IllumioObject], **kwargs) -> List[dict]: ...

        def bulk_update(self, objects_to_update: List[IllumioObject], **kwargs) -> List[dict]: ...

        @overload
        def bulk_delete(self, refs: List[str], **kwargs) -> List[dict]: ...
        @overload
        def bulk_delete(self, refs: List[Reference], **kwargs) -> List[dict]: ...
        @overload
        def bulk_delete(self, refs: List[dict], **kwargs) -> List[dict]: ...

    def __getattr__(self, name: str) -> _PCEObjectAPI: ...

    # Dynamic APIs stubbed here for auto-completion
    container_clusters: _PCEObjectAPI
    container_workload_profiles: _PCEObjectAPI
    enforcement_boundaries: _PCEObjectAPI
    events: _PCEObjectAPI
    ip_lists: _PCEObjectAPI
    label_groups: _PCEObjectAPI
    labels: _PCEObjectAPI
    pairing_profiles: _PCEObjectAPI
    rule_sets: _PCEObjectAPI
    rules: _PCEObjectAPI
    security_principals: _PCEObjectAPI
    service_bindings: _PCEObjectAPI
    services: _PCEObjectAPI
    users: _PCEObjectAPI
    vens: _PCEObjectAPI
    virtual_services: _PCEObjectAPI
    workloads: _PCEObjectAPI

    def get_default_ip_list(self, **kwargs) -> IPList: ...

    def generate_pairing_key(self, pairing_profile_href: str, **kwargs) -> str: ...

    def get_traffic_flows(self, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]: ...

    def get_traffic_flows_async(self, query_name: str, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]: ...

    def provision_policy_changes(self, change_description: str, hrefs: List[str], **kwargs) -> PolicyVersion: ...
