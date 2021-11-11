import json
import time
from typing import List

from requests import Session, Response

from .exceptions import IllumioApiException
from .policyobjects import VirtualService
from .explorer import TrafficQuery, TrafficFlow
from .util import IllumioEncoder


class PolicyComputeEngine:

    def __init__(self, domain_name, org_id='1', port='443', version='v2') -> None:
        self._session = Session()
        self._session.headers.update({'Accept': 'application/json'})
        self.base_url = "https://{}:{}/api/{}".format(domain_name, port, version)
        self.org_id = org_id

    def set_credentials(self, username: str, password: str) -> None:
        self._session.auth = (username, password)

    def _request(self, method: str, endpoint: str, include_org=True, **kwargs) -> Response:
        try:
            self._set_request_headers(**kwargs)
            url = self._build_url(endpoint, include_org)
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            raise IllumioApiException from e

    def _set_request_headers(self, is_async=False, **kwargs):
        headers = kwargs.get('headers', {})
        if 'data' in kwargs or 'json' in kwargs:
            kwargs['headers'] = {**headers, **{'Content-Type': 'application/json'}}
        if is_async:
            kwargs['headers'] = {**headers, **{'Prefer': 'respond-async'}}

    def _build_url(self, endpoint: str, include_org=True) -> str:
        org_str = '/orgs/{}'.format(self.org_id) if include_org else ''
        return '{}{}{}'.format(self.base_url, org_str, endpoint)

    def get_collection(self, endpoint: str, **kwargs) -> Response:
        try:
            self._set_request_headers(is_async=True, **kwargs)
            response = self._session.get(self._build_url(endpoint), **kwargs)
            response.raise_for_status()
            location = response.headers['Location']
            retry_after = int(response.headers['Retry-After'])

            while True:
                time.sleep(retry_after)
                response = self.get(location, include_org=False)
                response.raise_for_status()
                poll_result = response.json()
                poll_status = poll_result['status']

                if poll_status == 'failed':
                    raise Exception('Async collection job failed: ' + poll_result['result']['message'])
                elif poll_status == 'done':
                    collection_href = poll_result['result']['href']
                    break

            response = self.get(collection_href, include_org=False)
            response.raise_for_status()
            return response
        except Exception as e:
            raise IllumioApiException from e

    def get(self, endpoint: str, **kwargs) -> Response:
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Response:
        return self._request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Response:
        return self._request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Response:
        return self._request('DELETE', endpoint, **kwargs)

    def get_virtual_service(self, href: str, **kwargs) -> VirtualService:
        kwargs.pop('include_org', None)
        response = self.get(href, include_org=False, **kwargs)
        return VirtualService.from_json(response.json())

    def create_virtual_service(self, virtual_service: VirtualService, **kwargs) -> VirtualService:
        kwargs['json'] = json.dumps(virtual_service, cls=IllumioEncoder)
        response = self.post('/sec_policy/draft/virtual_services', **kwargs)
        return VirtualService.from_json(response.json())

    def get_traffic_flows(self, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]:
        kwargs['json'] = json.dumps(traffic_query, cls=IllumioEncoder)
        response = self.post('/traffic_flows/traffic_analysis_queries', **kwargs)
        print(response.json())
        return [TrafficFlow.from_json(flow) for flow in response.json()]

    def get_traffic_flows_async(self, query_name: str, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]:
        try:
            traffic_query.query_name = query_name
            kwargs['json'] = json.dumps(traffic_query, cls=IllumioEncoder)
            self._set_request_headers(is_async=True, **kwargs)
            response = self._session.post(self._build_url('/traffic_flows/async_queries'), **kwargs)
            response.raise_for_status()
            query_status = response.json()
            location = query_status['href']
            backoff = 0.1

            while True:
                backoff *= 2
                time.sleep(backoff)
                response = self.get(location, include_org=False)
                response.raise_for_status()
                poll_result = response.json()
                poll_status = poll_result['status']

                if poll_status == 'failed':
                    raise Exception('Async collection job failed: ' + poll_result['result']['message'])
                elif poll_status == 'completed':
                    collection_href = poll_result['result']
                    break

            response = self.get(collection_href, include_org=False)
            response.raise_for_status()
            return [TrafficFlow.from_json(flow) for flow in response.json()]
        except Exception as e:
            raise IllumioApiException from e
