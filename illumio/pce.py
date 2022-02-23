import time
from typing import List, Union

from requests import Session, Response

from .secpolicy import PolicyChangeset, PolicyVersion
from .exceptions import IllumioApiException
from .policyobjects import (
    IPList,
    ServiceBinding,
    VirtualService
)
from .explorer import TrafficQuery, TrafficFlow
from .rules import Ruleset, Rule, EnforcementBoundary
from .util import EnforcementMode, ACTIVE, DRAFT, ANY_IP_LIST_NAME, WORKLOAD_BULK_UPDATE_MAX
from .workloads import Workload


class PolicyComputeEngine:

    def __init__(self, domain_name, org_id='1', port='443', version='v2') -> None:
        self._session = Session()
        self._session.headers.update({'Accept': 'application/json'})
        self.base_url = "https://{}:{}/api/{}".format(domain_name, port, version)
        self.org_id = org_id

    def set_credentials(self, username: str, password: str) -> None:
        self._session.auth = (username, password)

    def set_proxies(self, http_proxy: str = None, https_proxy: str = None) -> None:
        self._session.proxies.update({'http': http_proxy, 'https': https_proxy})

    def _request(self, method: str, endpoint: str, include_org=True, **kwargs) -> Response:
        try:
            response = None  # avoid reference before assignment errors in case of cxn failure
            url = self._build_url(endpoint, include_org)
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            message = str(e)
            # Response objects are falsy if the request failed so do a null check
            if response is not None and response.headers.get('Content-Type', '') == 'application/json':
                message = "API call returned error code {}. Errors:".format(response.status_code)
                for error in response.json():
                    if error and 'token' in error and 'message' in error:
                        message += '\n{}: {}'.format(error['token'], error['message'])
                    elif error and 'error' in error:
                        message += '\n{}'.format(error['error'])
            raise IllumioApiException(message) from e

    def _build_url(self, endpoint: str, include_org=True) -> str:
        org_str = '/orgs/{}'.format(self.org_id) if include_org else ''
        return '{}{}{}'.format(self.base_url, org_str, endpoint)

    def get_collection(self, endpoint: str, **kwargs) -> Response:
        try:
            headers = kwargs.get('headers', {})
            kwargs['headers'] = {**headers, **{'Prefer': 'respond-async'}}
            response = self._session.get(self._build_url(endpoint), **kwargs)
            response.raise_for_status()
            location = response.headers['Location']
            retry_after = int(response.headers['Retry-After'])

            collection_href = self._async_poll(location, retry_after)

            response = self.get(collection_href, include_org=False)
            response.raise_for_status()
            return response
        except Exception as e:
            raise IllumioApiException from e

    def _async_poll(self, job_location: str, retry_time: Union[int, float] = 1.) -> str:
        while True:
            time.sleep(retry_time)
            retry_time *= 1.5  # slight backoff to avoid spamming the PCE for long-running jobs
            response = self.get(job_location, include_org=False)
            response.raise_for_status()
            poll_result = response.json()
            poll_status = poll_result['status']

            if poll_status == 'failed':
                raise Exception('Async collection job failed: ' + poll_result['result']['message'])
            elif poll_status == 'completed':
                # traffic flow async jobs
                collection_href = poll_result['result']
                break
            elif poll_status == 'done':
                # policy object collection jobs
                collection_href = poll_result['result']['href']
                break
        return collection_href

    def get(self, endpoint: str, **kwargs) -> Response:
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Response:
        headers = kwargs.get('headers', {})
        kwargs['headers'] = {**headers, **{'Content-Type': 'application/json'}}
        return self._request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Response:
        headers = kwargs.get('headers', {})
        kwargs['headers'] = {**headers, **{'Content-Type': 'application/json'}}
        return self._request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Response:
        return self._request('DELETE', endpoint, **kwargs)

    def check_connection(self, **kwargs) -> bool:
        try:
            self.get('/health', include_org=False, **kwargs)
            return True
        except IllumioApiException:
            return False

    def _get_by_name(self, name: str, object_type, **kwargs):
        params = kwargs.get('params', {})
        kwargs['params'] = {**params, **{'name': name}}
        results = []
        response = self.get('/sec_policy/{}/{}'.format(ACTIVE, object_type), **kwargs)
        results += list(response.json())
        # a draft version of an active object will still be returned from GET queries
        # against the /draft/ policy version endpoints. because of this, we check and
        # only return the active version if it exists
        response = self.get('/sec_policy/{}/{}'.format(DRAFT, object_type), **kwargs)
        active_objects = {active_object['name'] for active_object in results}
        for draft_object in response.json():
            if draft_object['name'] not in active_objects:
                results.append(draft_object)
        return results

    def get_virtual_service(self, href: str, **kwargs) -> VirtualService:
        response = self.get(href, include_org=False, **kwargs)
        return VirtualService.from_json(response.json())

    def get_virtual_services_by_name(self, name: str, **kwargs) -> List[VirtualService]:
        results = self._get_by_name(name, object_type='virtual_services', **kwargs)
        return [VirtualService.from_json(o) for o in results]

    def create_virtual_service(self, virtual_service: VirtualService, **kwargs) -> VirtualService:
        kwargs['json'] = virtual_service.to_json()
        response = self.post('/sec_policy/draft/virtual_services', **kwargs)
        return VirtualService.from_json(response.json())

    def create_service_binding(self, service_binding: ServiceBinding, **kwargs) -> ServiceBinding:
        kwargs['json'] = [service_binding.to_json()]
        response = self.post('/service_bindings', **kwargs)
        binding = response.json()[0]
        if binding['status'] == 'created':
            service_binding.href = binding['href']
            return service_binding
        raise IllumioApiException("Service binding creation failed with status: {}".format(binding['status']))

    def create_service_bindings(self, service_bindings: List[ServiceBinding], **kwargs) -> dict:
        kwargs['json'] = [service_binding.to_json() for service_binding in service_bindings]
        response = self.post('/service_bindings', **kwargs)
        # if one or more service bindings fail to create - even if all of them
        # fail - a 201 response is returned with error statuses for each failing
        # binding. we rewrap the response to simplify processing
        results = {"service_bindings": [], "errors": []}
        for binding in response.json():
            if binding['status'] == 'created':
                results['service_bindings'].append(ServiceBinding(href=binding['href']))
            else:
                results['errors'].append({'error': binding['status']})
        return results

    def get_ip_list(self, href: str, **kwargs) -> IPList:
        response = self.get(href, include_org=False, **kwargs)
        return IPList.from_json(response.json())

    def get_ip_lists_by_name(self, name: str, **kwargs) -> List[IPList]:
        results = self._get_by_name(name, object_type='ip_lists', **kwargs)
        return [IPList.from_json(o) for o in results]

    def get_default_ip_list(self, **kwargs) -> IPList:
        params = kwargs.get('params', {})
        kwargs['params'] = {**params, **{'name': ANY_IP_LIST_NAME}}
        response = self.get('/sec_policy/active/ip_lists', **kwargs)
        return IPList.from_json(response.json()[0])

    def get_rulesets_by_name(self, name: str, **kwargs) -> List[Ruleset]:
        results = self._get_by_name(name, object_type='rule_sets', **kwargs)
        return [Ruleset.from_json(o) for o in results]

    def create_ruleset(self, ruleset: Ruleset, **kwargs) -> Ruleset:
        if ruleset.scopes is None:
            ruleset.scopes = []
        kwargs['json'] = ruleset.to_json()
        response = self.post('/sec_policy/draft/rule_sets', **kwargs)
        return Ruleset.from_json(response.json())

    def create_rule(self, ruleset_href: str, rule: Rule, **kwargs) -> Rule:
        if rule.enabled is None:
            rule.enabled = True
        kwargs['json'] = rule.to_json()
        endpoint = '{}/sec_rules'.format(ruleset_href)
        response = self.post(endpoint, include_org=False, **kwargs)
        return Rule.from_json(response.json())

    def get_enforcement_boundaries_by_name(self, name: str, **kwargs) -> List[EnforcementBoundary]:
        results = self._get_by_name(name, object_type='enforcement_boundaries', **kwargs)
        return [EnforcementBoundary.from_json(o) for o in results]

    def create_enforcement_boundary(self, enforcement_boundary: EnforcementBoundary, **kwargs) -> EnforcementBoundary:
        kwargs['json'] = enforcement_boundary.to_json()
        response = self.post('/sec_policy/draft/enforcement_boundaries', **kwargs)
        return EnforcementBoundary.from_json(response.json())

    def get_workload(self, href: str, **kwargs) -> Workload:
        response = self.get(href, include_org=False, **kwargs)
        return Workload.from_json(response.json())

    def get_workloads(self, **kwargs) -> List[Workload]:
        # the Illumio APIs don't use pagination, opting instead for an async
        # batch GET approach that can be slow. instead, we accommodate large
        # numbers of workloads by first fetching 0 results to get the
        # X-Total-Count in the response, then fetching all results synchronously.
        # this approach should have an advantage over an async call up to over
        # 100,000 workloads
        params = kwargs.get('params', {})

        if 'max_results' not in params:
            kwargs['params'] = {**params, **{'max_results': 0}}
            response = self.get('/workloads', **kwargs)
            filtered_workload_count = response.headers['X-Total-Count']
            kwargs['params'] = {**params, **{'max_results': int(filtered_workload_count)}}

        response = self.get('/workloads', **kwargs)
        return [Workload.from_json(o) for o in response.json()]

    def update_workload_enforcement_modes(self, enforcement_mode: EnforcementMode, workloads: List[Workload], **kwargs) -> dict:
        results = {"workloads": [], "errors": []}
        while workloads:
            kwargs['json'] = [{'href': workload.href, 'enforcement_mode': enforcement_mode.value} for workload in workloads[:WORKLOAD_BULK_UPDATE_MAX]]
            workloads = workloads[WORKLOAD_BULK_UPDATE_MAX:]
            response = self.put('/workloads/bulk_update', **kwargs)
            for binding in response.json():
                if binding['status'] == 'updated':
                    results['workloads'].append(Workload(href=binding['href']))
                else:
                    results['errors'].append({'error': binding['status']})
        return results

    def get_traffic_flows(self, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]:
        kwargs['json'] = traffic_query.to_json()
        response = self.post('/traffic_flows/traffic_analysis_queries', **kwargs)
        return [TrafficFlow.from_json(flow) for flow in response.json()]

    def get_traffic_flows_async(self, query_name: str, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]:
        try:
            traffic_query.query_name = query_name
            kwargs['json'] = traffic_query.to_json()
            headers = kwargs.get('headers', {})
            kwargs['headers'] = {**headers, **{'Content-Type': 'application/json', 'Prefer': 'respond-async'}}
            response = self._session.post(self._build_url('/traffic_flows/async_queries'), **kwargs)
            response.raise_for_status()
            query_status = response.json()
            location = query_status['href']

            collection_href = self._async_poll(location)

            response = self.get(collection_href, include_org=False)
            response.raise_for_status()
            return [TrafficFlow.from_json(flow) for flow in response.json()]
        except Exception as e:
            raise IllumioApiException from e

    def provision_policy_changes(self, change_description: str, hrefs: List[str], **kwargs) -> PolicyVersion:
        policy_changeset = PolicyChangeset.build(hrefs)
        kwargs['json'] = {'update_description': change_description, 'change_subset': policy_changeset.to_json()}
        response = self.post('/sec_policy', **kwargs)
        return PolicyVersion.from_json(response.json())


__all__ = ['PolicyComputeEngine']
