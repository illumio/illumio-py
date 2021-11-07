import time

from requests import Session, Response

from .exceptions import IllumioApiException
from .policyobjects import VirtualService


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
            if 'data' in kwargs or 'json' in kwargs:
                headers = kwargs.get('headers', {})
                kwargs['headers'] = {**headers, **{'Content-Type': 'application/json'}}
            url = self._build_url(endpoint, include_org)
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            raise IllumioApiException from e

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

            while True:
                time.sleep(retry_after)
                response = self.get(location, include_org=False)
                poll_result = response.json()
                poll_status = poll_result['status']

                if poll_status == 'failed':
                    raise Exception('Async collection job failed: ' + poll_result['result']['message'])
                elif poll_status == 'done':
                    collection_href = poll_result['result']['href']
                    break
            return self.get(collection_href, include_org=False)
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
        kwargs['json'] = virtual_service.to_json()
        response = self.post('/sec_policy/draft/virtual_services', **kwargs)
        return VirtualService.from_json(response.json())
