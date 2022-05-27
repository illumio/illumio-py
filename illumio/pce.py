# -*- coding: utf-8 -*-

"""This module provides the core PolicyComputeEngine class for communicating with the PCE.

Usage:
    >>> from illumio import PolicyComputeEngine
    >>> pce = PolicyComputeEngine('my.pce.com', port='8443', org_id='12')
    >>> pce.set_credentials('<API_KEY>', '<API_SECRET>')
    >>> workloads = pce.get_workloads(
    ...     params={
    ...         'managed': True,
    ...         'enforcement_mode': 'visibility_only'
    ...     }
    ... )
    >>> workloads
    [
        Workload(href='/orgs/12/workloads/c754a713-2bde-4427-af1f-bff145be509b', ...),
        ...
    ]

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
import time
from typing import List, Union

from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .secpolicy import PolicyChangeset, PolicyVersion
from .exceptions import IllumioApiException
from .policyobjects import (
    IPList,
    ServiceBinding,
    VirtualService
)
from .explorer import TrafficQuery, TrafficFlow
from .rules import Ruleset, Rule, EnforcementBoundary
from .util import (
    deprecated,
    convert_active_href_to_draft,
    parse_url,
    IllumioObject,
    PolicyObjectType,
    EnforcementMode,
    ACTIVE,
    DRAFT,
    ANY_IP_LIST_NAME,
    WORKLOAD_BULK_UPDATE_MAX
)
from .workloads import Workload, PairingProfile


class PolicyComputeEngine:
    """The REST client core for the Illumio Policy Compute Engine.

    Contains request logic for API calls and handles the HTTP(S) connection to the PCE.

    Attributes:
        base_url: the base URL for API calls to the PCE. Has the form
            http[s]://<DOMAIN_NAME>:<PORT>/api/<API_VERSION>
        org_id: the PCE organization ID.
    """

    def __init__(self, url: str, port: str = '443', version: str = 'v2', org_id: str = '1') -> None:
        """Initializes the PCE REST client.

        Args:
            url (str): PCE URL. May include http:// or https:// as the protocol.
            port (str, optional): PCE http(s) port. Defaults to '443'.
            version (str, optional): The PCE API version to use. Defaults to 'v2'.
            org_id (str, optional): The PCE organization ID. Defaults to '1'.
        """
        self._session = Session()
        self._session.headers.update({'Accept': 'application/json'})
        protocol, url = parse_url(url)
        self.base_url = "{}://{}:{}/api/{}".format(protocol, url, port, version)
        self.org_id = org_id
        self._setup_retry()

    def _setup_retry(self):
        """Configures `requests.Session` retry defaults"""
        retry_strategy = Retry(
            total=5,  # retry up to 5 times
            # {backoff} * (2 ** ({retry count} - 1))
            # 1, 2, 4, 8, 16 (seconds)
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def set_credentials(self, username: str, password: str) -> None:
        """Sets username and password values to authenticate with the PCE.

        The provided credentials can be either user credentials or an API key/secret pair.

        Args:
            username (str): username or API key.
            password (str): password or API secret.
        """
        self._session.auth = (username, password)

    def set_proxies(self, http_proxy: str = None, https_proxy: str = None) -> None:
        """Sets proxy information in the request session.

        Args:
            http_proxy (str, optional): HTTP proxy URI. Defaults to None.
            https_proxy (str, optional): HTTPS proxy URI. Defaults to None.
        """
        self._session.proxies.update({'http': http_proxy, 'https': https_proxy})

    def _request(self, method: str, endpoint: str, include_org=True, **kwargs) -> Response:
        """Makes an API call to the PCE.

        Args:
            method (str): the HTTP request method. Supports the same verbs as `requests.request`.
            endpoint (str): the API endpoint to call.
            include_org (bool, optional): whether or not to include /orgs/ in the API call.
                Defaults to True.

        Raises:
            IllumioApiException: if the response is unsuccessful (status code >399).

        Returns:
            requests.Response: the `Response` object returned from a successful request.
        """
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
        """Constructs request URL with optional organization ID."""
        org_str = '/orgs/{}'.format(self.org_id) if include_org else ''
        return self.base_url + org_str + endpoint

    def get(self, endpoint: str, **kwargs) -> Response:
        """Makes a GET call to a given PCE endpoint.

        Additional keyword arguments are passed to the requests call.

        Args:
            endpoint (str): the PCE endpoint to call.

        Returns:
            requests.Response: the `Response` object returned from a successful request.
        """
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Response:
        """Makes a POST call to a given PCE endpoint.

        Appends 'Content-Type: application/json' to the request headers by default.
        Additional keyword arguments are passed to the requests call.

        Args:
            endpoint (str): the PCE endpoint to call.

        Returns:
            requests.Response: the `Response` object returned from a successful request.
        """
        headers = kwargs.get('headers', {})
        kwargs['headers'] = {**headers, **{'Content-Type': 'application/json'}}
        return self._request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Response:
        """Makes a PUT call to a given PCE endpoint.

        Appends 'Content-Type: application/json' to the request headers by default.
        Additional keyword arguments are passed to the requests call.

        Args:
            endpoint (str): the PCE endpoint to call.

        Returns:
            requests.Response: the `Response` object returned from a successful request.
        """
        headers = kwargs.get('headers', {})
        kwargs['headers'] = {**headers, **{'Content-Type': 'application/json'}}
        return self._request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Response:
        """Makes a DELETE call to a given PCE endpoint.

        Additional keyword arguments are passed to the requests call.

        Args:
            endpoint (str): the PCE endpoint to call.

        Returns:
            requests.Response: the `Response` object returned from a successful request.
        """
        return self._request('DELETE', endpoint, **kwargs)

    def get_collection(self, endpoint: str, **kwargs) -> Response:
        """Uses the PCE's asynchronous job logic to retrieve a collection of objects.

        NOTE: for large collections (surpassing 10,000 objects), this function will be extremely
        slow - it is recommended that callers use query filters or the max_results parameter to limit
        the number of results in the collection.

        Args:
            endpoint (str): the PCE endpoint to call.

        Raises:
            IllumioApiException: if an error message (>399) status code is returned.

        Returns:
            requests.Response: the `Response` object returned from a successful request.
        """
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
        """Polls the PCE for an async job's status until it completes or times out.

        The poll-wait loop uses the Retry-After time from the job submission  request
        or a default of 1 second, with a 1.5x backoff.

        Args:
            job_location (str): URL of the job to poll.
            retry_time (Union[int, float], optional): base Retry-After time. Defaults to 1 second.

        Raises:
            Exception: if the job returns a 'failed' status.

        Returns:
            str: the HREF path of the completed collection document.
        """
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

    def check_connection(self, **kwargs) -> bool:
        """Makes a GET request to the PCE /health endpoint.

        Additional keyword arguments are passed to the requests call.

        Returns:
            bool: True if the call is successful, otherwise False.
        """
        try:
            self.get('/health', include_org=False, **kwargs)
            return True
        except IllumioApiException:
            return False

    def _get_policy_objects(self, object_type: PolicyObjectType, **kwargs) -> List[IllumioObject]:
        """Retrieves all policy objects of a given type.

        Args:
            object_type (PolicyObjectType): policy object type enum.

        Returns:
            List[IllumioObject]: list of decoded draft and active policy objects of the
                given type. Active records override draft if both exist for a given object.
        """
        results = []
        response = self.get('/sec_policy/{}/{}'.format(ACTIVE, object_type.endpoint), **kwargs)
        results += list(response.json())
        # a draft version of an active object will still be returned from GET queries
        # against the /draft/ policy version endpoints. because of this, we check and
        # only return the active version if it exists
        response = self.get('/sec_policy/{}/{}'.format(DRAFT, object_type.endpoint), **kwargs)
        active_objects = {active_object['name'] for active_object in results}
        for draft_object in response.json():
            if draft_object['name'] not in active_objects:
                results.append(draft_object)
        return results

    def get_virtual_service(self, href: str, **kwargs) -> VirtualService:
        """Retrieves a virtual service from the PCE using its HREF.

        Args:
            href (str): the HREF of the virtual service object to fetch.

        Returns:
            VirtualService: the decoded virtual service.
        """
        response = self.get(href, include_org=False, **kwargs)
        return VirtualService.from_json(response.json())

    def get_virtual_services(self, **kwargs) -> List[VirtualService]:
        """Retrieves virtual service objects from the PCE based on the given parameters.

        Keyword arguments to this function are passed to the `requests.get` call.
        See https://docs.illumio.com/core/21.5/API-Reference/index.html#get-virtual-services
        for details on filter parameters for virtual service collection queries.

        Usage:
            >>> virtual_services = pce.get_virtual_services(
            ...     params={
            ...         'name': 'VS-'
            ...     }
            ... )
            >>> virtual_services
            [
                VirtualService(
                    href='/orgs/1/sec_policy/active/virtual_services/9177c75f-7b21-4bf0-8c16-2c47c1ca3252',
                    name='VS-LAB-SERVICES'
                    ...
                ),
                ...
            ]

        Returns:
            List[VirtualService]: the returned list of decoded virtual services.
        """
        results = self._get_policy_objects(object_type=PolicyObjectType.VIRTUAL_SERVICE, **kwargs)
        return [VirtualService.from_json(o) for o in results]

    @deprecated(deprecated_in='0.8.0')
    def get_virtual_services_by_name(self, name: str, **kwargs) -> List[VirtualService]:
        """DEPRECATED (v0.8.0). Use get_virtual_services with params={'name': name} instead.

        Retrieves virtual service objects from the PCE by name.

        Supports partial matches, e.g., "VS-" will match "VS-LAB-SERVICES".

        Args:
            name (str): full or partial virtual service name to search by.

        Returns:
            List[VirtualService]: the returned list of decoded virtual services.
        """
        params = kwargs.get('params', {})
        kwargs['params'] = {**params, **{'name': name}}
        results = self._get_policy_objects(object_type=PolicyObjectType.VIRTUAL_SERVICE, **kwargs)
        return [VirtualService.from_json(o) for o in results]

    def create_virtual_service(self, virtual_service: VirtualService, **kwargs) -> VirtualService:
        """Creates a virtual service object in the PCE.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#create-a-virtual-service
        for details on POST body parameters when creating virtual services.

        Usage:
            >>> from illumio.policyobjects import VirtualService
            >>> virtual_service = VirtualService(
            ...     name='VS-LAB-SERVICES',
            ...     service_ports=[
            ...         ServicePort(port=80, proto='tcp')
            ...         ServicePort(port=443, proto='tcp')
            ...     ]
            ... )
            >>> virtual_service = pce.create_virtual_service(virtual_service)
            >>> virtual_service
            VirtualService(
                href='/orgs/1/sec_policy/active/virtual_services/9177c75f-7b21-4bf0-8c16-2c47c1ca3252',
                name='VS-LAB-SERVICES',
                service_ports=[
                    ...
                ]
            )

        Args:
            virtual_service (VirtualService): the virtual service to create.

        Returns:
            VirtualService: the re-encoded virtual service object with valid HREF.
        """
        kwargs['json'] = virtual_service.to_json()
        response = self.post('/sec_policy/draft/virtual_services', **kwargs)
        return VirtualService.from_json(response.json())

    @deprecated(deprecated_in='0.8.2')
    def create_service_binding(self, service_binding: ServiceBinding, **kwargs) -> ServiceBinding:
        """DEPRECATED (v0.8.2). Use create_service_bindings instead.

        Binds a workload to a virtual service in the PCE.

        Args:
            service_binding (ServiceBinding): the service binding object to create.

        Raises:
            IllumioApiException: if creation is unsuccessful.

        Returns:
            ServiceBinding: the re-encoded service binding object with valid HREF.
        """
        kwargs['json'] = [service_binding.to_json()]
        response = self.post('/service_bindings', **kwargs)
        binding = response.json()[0]
        if binding['status'] == 'created':
            service_binding.href = binding['href']
            return service_binding
        raise IllumioApiException('Service binding creation failed with status: {}'.format(binding['status']))

    def create_service_bindings(self, service_bindings: List[ServiceBinding], **kwargs) -> dict:
        """Binds one or more workloads to a virtual service in the PCE.

        If one or more service bindings fail to create - even if all of them
        fail - a 201 response is returned with error statuses for each failing
        binding. Due to this, the response is wrapped to simplify processing.

        Usage:
            >>> from illumio.policyobjects import ServiceBinding
            >>> virtual_service_ref = Reference(
            ...     href='/orgs/1/sec_policy/active/virtual_services/9177c75f-7b21-4bf0-8c16-2c47c1ca3252'
            ... )
            >>> workload = pce.get_workload(href='/orgs/1/workloads/a1a2bd2f-b74b-4068-a177-11b0cb1c92c4')
            >>> service_bindings = pce.create_service_bindings(
            ...     service_bindings=[
            ...         ServiceBinding(
            ...             virtual_service=virtual_service_ref,
            ...             workload=workload
            ...         )
            ...     ]
            ... )
            >>> service_bindings
            {
                'service_bindings': [
                    ServiceBinding(
                        href='/orgs/1/service_bindings/7005192b-97a3-4072-96ab-d584544d032f',
                        virtual_service=Reference(
                            href='/orgs/1/sec_policy/active/virtual_services/9177c75f-7b21-4bf0-8c16-2c47c1ca3252'
                        ),
                        workload=Workload(
                            href='/orgs/1/workloads/a1a2bd2f-b74b-4068-a177-11b0cb1c92c4',
                            ...
                        ),
                        ...
                    )
                ],
                'errors': []
            }

        Args:
            service_bindings (List[ServiceBinding]): list of service binding
                objects to create. Each object is encoded as JSON for the POST
                request payload.

        Returns:
            dict: a dictionary containing a list of successfully created
                service bindings as well as any errors returned from the PCE.
                Has the form {'service_bindings': [], 'errors': []}.
        """
        kwargs['json'] = [service_binding.to_json() for service_binding in service_bindings]
        response = self.post('/service_bindings', **kwargs)
        results = {'service_bindings': [], 'errors': []}
        for binding in response.json():
            if binding['status'] == 'created':
                results['service_bindings'].append(ServiceBinding(href=binding['href']))
            else:
                results['errors'].append({'error': binding['status']})
        return results

    def get_ip_list(self, href: str, **kwargs) -> IPList:
        """Retrieves an IP list from the PCE using its HREF.

        Args:
            href (str): the HREF of the IP list object to fetch.

        Returns:
            IPList: the decoded IP list object.
        """
        response = self.get(href, include_org=False, **kwargs)
        return IPList.from_json(response.json())

    def get_ip_lists(self, **kwargs) -> List[IPList]:
        """Retrieves IP list objects from the PCE based on the given parameters.

        Keyword arguments to this function are passed to the `requests.get` call.
        See https://docs.illumio.com/core/21.5/API-Reference/index.html#get-ip-lists
        for details on filter parameters for IP list collection queries.

        Usage:
            >>> ip_lists = pce.get_ip_lists(
            ...     params={
            ...         'name': 'IPL-'
            ...     }
            ... )
            >>> ip_lists
            [
                IPList(
                    href='/orgs/1/sec_policy/active/ip_lists/5',
                    name='IPL-INTERNAL',
                    ...
                ),
                ...
            ]

        Returns:
            List[IPList]: the returned list of decoded IP lists.
        """
        results = self._get_policy_objects(object_type=PolicyObjectType.IP_LIST, **kwargs)
        return [IPList.from_json(o) for o in results]

    @deprecated(deprecated_in='0.8.0')
    def get_ip_lists_by_name(self, name: str, **kwargs) -> List[IPList]:
        """DEPRECATED (v0.8.0). Use get_ip_lists with params={'name': name} instead.

        Retrieves IP list objects from the PCE by name.

        Supports partial matches, e.g., "IPL-" will match "IPL-INTERNAL".

        Args:
            name (str): full or partial IP list name to search by.

        Returns:
            List[IPList]: the returned list of decoded IP lists.
        """
        params = kwargs.get('params', {})
        kwargs['params'] = {**params, **{'name': name}}
        results = self._get_policy_objects(object_type=PolicyObjectType.IP_LIST, **kwargs)
        return [IPList.from_json(o) for o in results]

    def get_default_ip_list(self, **kwargs) -> IPList:
        """Retrieves the "Any (0.0.0.0/0 and ::/0)" default global IP list.

        Returns:
            IPList: decoded object representing the default global IP list.
        """
        params = kwargs.get('params', {})
        # retrieve by name as each org will use a different ID
        kwargs['params'] = {**params, **{'name': ANY_IP_LIST_NAME}}
        response = self.get('/sec_policy/active/ip_lists', **kwargs)
        return IPList.from_json(response.json()[0])

    def create_ip_list(self, ip_list: IPList, **kwargs) -> IPList:
        """Creates an IP list object in the PCE.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#create-an-ip-list
        for details on POST body parameters when creating IP lists.

        Usage:
            >>> from illumio.policyobjects import IPList
            >>> ip_list = IPList(
            ...     name='IPL-INTERNAL',
            ...     ip_ranges=[
            ...         IPRange(from_ip='10.0.0.0/8')
            ...     ]
            ... )
            >>> ip_list = pce.create_ip_list(ip_list)
            >>> ip_list
            IPList(
                href='/orgs/1/sec_policy/draft/ip_lists/5',
                name='IPL-INTERNAL',
                ip_ranges=[
                    IPRange(from_ip='10.0.0.0/8')
                ]
            )

        Args:
            ip_list (IPList): the IP list to create.

        Returns:
            IPList: the re-encoded IP list object with valid HREF.
        """
        kwargs['json'] = ip_list.to_json()
        response = self.post('/sec_policy/draft/ip_lists', **kwargs)
        return IPList.from_json(response.json())

    def get_ruleset(self, href: str, **kwargs) -> Ruleset:
        """Retrieves a ruleset from the PCE using its HREF.

        Args:
            href (str): the HREF of the ruleset object to fetch.

        Returns:
            Ruleset: the decoded ruleset object.
        """
        response = self.get(href, include_org=False, **kwargs)
        return Ruleset.from_json(response.json())

    def get_rulesets(self, **kwargs) -> List[Ruleset]:
        """Retrieves ruleset objects from the PCE based on the given parameters.

        Keyword arguments to this function are passed to the `requests.get` call.
        See https://docs.illumio.com/core/21.5/API-Reference/index.html#get-rulesets
        for details on filter parameters for ruleset collection queries.

        Usage:
            >>> rulesets = pce.get_rulesets(
            ...     params={
            ...         'name': 'RS-'
            ...     }
            ... )
            >>> rulesets
            [
                Ruleset(
                    href='/orgs/1/sec_policy/active/rule_sets/19',
                    name='RS-RINGFENCE',
                    ...
                ),
                ...
            ]

        Returns:
            List[Ruleset]: the returned list of decoded rulesets.
        """
        results = self._get_policy_objects(object_type=PolicyObjectType.RULESET, **kwargs)
        return [Ruleset.from_json(o) for o in results]

    @deprecated(deprecated_in='0.8.0')
    def get_rulesets_by_name(self, name: str, **kwargs) -> List[Ruleset]:
        """DEPRECATED (v0.8.0). Use get_rulesets with params={'name': name} instead.

        Retrieves ruleset objects from the PCE by name.

        Supports partial matches, e.g., "RS-" will match "RS-RINGFENCE".

        Args:
            name (str): full or partial ruleset name to search by.

        Returns:
            List[Ruleset]: the returned list of decoded rulesets.
        """
        params = kwargs.get('params', {})
        kwargs['params'] = {**params, **{'name': name}}
        results = self._get_policy_objects(object_type=PolicyObjectType.RULESET, **kwargs)
        return [Ruleset.from_json(o) for o in results]

    def create_ruleset(self, ruleset: Ruleset, **kwargs) -> Ruleset:
        """Creates a ruleset object in the PCE.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#create-a-ruleset
        for details on POST body parameters when creating rulesets.

        Usage:
            >>> from illumio.rules import Ruleset
            >>> ruleset = Ruleset(name='RS-RINGFENCE')
            >>> ruleset = pce.create_ruleset(ruleset)
            >>> ruleset
            Ruleset(
                href='/orgs/1/sec_policy/draft/rule_sets/19',
                name='RS-RINGFENCE'
            )

        Args:
            ruleset (Ruleset): the ruleset to create.

        Returns:
            Ruleset: the re-encoded ruleset object with valid HREF.
        """
        if ruleset.scopes is None:
            ruleset.scopes = []
        kwargs['json'] = ruleset.to_json()
        response = self.post('/sec_policy/draft/rule_sets', **kwargs)
        return Ruleset.from_json(response.json())

    def create_rule(self, ruleset_href: str, rule: Rule, **kwargs) -> Rule:
        """Creates a rule object in the PCE.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#create-a-security-rule
        for details on POST body parameters when creating rules.

        Rules can't be created in active rulesets, so if an active ruleset HREF
        is provided, it is assumed the user wants to modify its draft version.

        Usage:
            >>> from illumio.rules import Rule
            >>> virtual_service_href = '/orgs/1/sec_policy/active/virtual_services/9177c75f-7b21-4bf0-8c16-2c47c1ca3252'
            >>> any_ip_list = pce.get_default_ip_list()
            >>> rule = Rule.build(
            ...     providers=[virtual_service_href],
            ...     consumers=[any_ip_list.href],
            ...     ingress_services=[],
            ...     resolve_providers_as=['virtual_services'],
            ...     resolve_consumers_as=['workloads']
            ... )
            >>> ruleset = Ruleset(name='RS-LAB-ALLOWLIST')
            >>> ruleset = pce.create_ruleset(ruleset)
            >>> rule = pce.create_rule(
            ...     ruleset_href=ruleset.href,
            ...     rule=rule
            ... )
            >>> rule
            Rule(
                href='/orgs/1/sec_policy/rule_sets/19/rules/sec_rules/1',
                enabled=True,
                providers=[
                    Actor(
                        virtual_service=Reference(
                            href='/orgs/1/sec_policy/active/virtual_services/9177c75f-7b21-4bf0-8c16-2c47c1ca3252'
                        ),
                        ...
                    )
                ],
                consumers=[
                    Actor(
                        ip_list=Reference(
                            href='/orgs/1/sec_policy/active/ip_lists/1'
                        ),
                        ...
                    )
                ],
                ingress_services=[],
                resolve_labels_as=LabelResolutionBlock(
                    providers=['virtual_services'],
                    consumers=['workloads']
                ),
                ...
            )


        Args:
            ruleset_href (str): the ruleset to create the rule in.
            rule (Rule): the rule to create.

        Returns:
            Rule: the re-encoded rule object with valid HREF.
        """
        if rule.enabled is None:
            rule.enabled = True
        kwargs['json'] = rule.to_json()
        ruleset_href = convert_active_href_to_draft(ruleset_href)
        endpoint = '{}/sec_rules'.format(ruleset_href)
        response = self.post(endpoint, include_org=False, **kwargs)
        return Rule.from_json(response.json())

    def get_enforcement_boundary(self, href: str, **kwargs) -> EnforcementBoundary:
        """Retrieves an enforcement boundary from the PCE using its HREF.

        Args:
            href (str): the HREF of the enforcement boundary object to fetch.

        Returns:
            EnforcementBoundary: the decoded enforcement boundary object.
        """
        response = self.get(href, include_org=False, **kwargs)
        return EnforcementBoundary.from_json(response.json())

    def get_enforcement_boundaries(self, **kwargs) -> List[EnforcementBoundary]:
        """Retrieves enforcement boundary objects from the PCE based on the given parameters.

        Keyword arguments to this function are passed to the `requests.get` call.
        See https://docs.illumio.com/core/21.5/API-Reference/index.html#tocSsec_policy_enforcement_boundaries_get
        for details on filter parameters for enforcement boundary collection queries.

        Usage:
            >>> enforcement_boundaries = pce.get_enforcement_boundaries(
            ...     params={
            ...         'name': 'EB-'
            ...     }
            ... )
            >>> enforcement_boundaries
            [
                EnforcementBoundary(
                    href='/orgs/1/sec_policy/active/enforcement_boundary/8',
                    name='EB-BLOCK-RDP',
                    ...
                ),
                ...
            ]

        Returns:
            List[EnforcementBoundary]: the returned list of decoded enforcement boundaries.
        """
        results = self._get_policy_objects(object_type=PolicyObjectType.ENFORCEMENT_BOUNDARY, **kwargs)
        return [EnforcementBoundary.from_json(o) for o in results]

    @deprecated(deprecated_in='0.8.0')
    def get_enforcement_boundaries_by_name(self, name: str, **kwargs) -> List[EnforcementBoundary]:
        """DEPRECATED (v0.8.0). Use get_enforcement_boundaries with params={'name': name} instead.

        Retrieves enforcement boundary objects from the PCE by name.

        Supports partial matches, e.g., "EB-" will match "EB-BLOCK-RDP".

        Args:
            name (str): full or partial enforcement boundary name to search by.

        Returns:
            List[EnforcementBoundary]: the returned list of decoded
                enforcement boundaries.
        """
        params = kwargs.get('params', {})
        kwargs['params'] = {**params, **{'name': name}}
        results = self._get_policy_objects(object_type=PolicyObjectType.ENFORCEMENT_BOUNDARY, **kwargs)
        return [EnforcementBoundary.from_json(o) for o in results]

    def create_enforcement_boundary(self, enforcement_boundary: EnforcementBoundary, **kwargs) -> EnforcementBoundary:
        """Creates an enforcement boundary object in the PCE.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#tocSsec_policy_enforcement_boundaries_post
        for details on POST body parameters when creating enforcement boundaries.

        Usage:
            >>> from illumio.rules import EnforcementBoundary, AMS
            >>> any_ip_list = pce.get_default_ip_list()
            >>> enforcement_boundary = EnforcementBoundary.build(
            ...     name='EB-BLOCK-RDP',
            ...     providers=[AMS],  # the special 'ams' literal denotes all workloads
            ...     consumers=[any_ip_list.href],
            ...     ingress_services=[
            ...         {'port': 3389, 'proto': 'tcp'},
            ...         {'port': 3389, 'proto': 'udp'},
            ...     ]
            ... )
            >>> enforcement_boundary = pce.create_enforcement_boundary(enforcement_boundary)
            >>> enforcement_boundary
            EnforcementBoundary(
                href='/orgs/1/sec_policy/draft/enforcement_boundary/8',
                name='EB-BLOCK-RDP',
                providers=[
                    Actor(
                        actors='ams',
                        ...
                    )
                ],
                consumers=[
                    Actor(
                        ip_list=Reference(
                            href='/orgs/1/sec_policy/active/ip_lists/1'
                        ),
                        ...
                    )
                ],
                ingress_services=[
                    ServicePort(port=3389, proto=6),
                    ServicePort(port=3389, proto=17)
                ],
                ...
            )

        Args:
            enforcement_boundary (EnforcementBoundary): the enforcement boundary to create.

        Returns:
            EnforcementBoundary: the re-encoded enforcement boundary object with valid HREF.
        """
        kwargs['json'] = enforcement_boundary.to_json()
        response = self.post('/sec_policy/draft/enforcement_boundaries', **kwargs)
        return EnforcementBoundary.from_json(response.json())

    def get_pairing_profile(self, href: str, **kwargs) -> PairingProfile:
        """Retrieves a pairing profile from the PCE using its HREF.

        Args:
            href (str): the HREF of the pairing profile object to fetch.

        Returns:
            PairingProfile: the decoded pairing profile object.
        """
        response = self.get(href, include_org=False, **kwargs)
        return PairingProfile.from_json(response.json())

    def get_pairing_profiles(self, **kwargs) -> List[PairingProfile]:
        """Retrieves pairing profile objects from the PCE based on the given parameters.

        Keyword arguments to this function are passed to the `requests.get` call.
        See https://docs.illumio.com/core/21.5/API-Reference/index.html#tocSpairing_profiles_get
        for details on filter parameters for pairing profile collection queries.

        Usage:
            >>> pairing_profiles = pce.get_pairing_profiles(
            ...     params={
            ...         'name': 'PP-'
            ...     }
            ... )
            >>> pairing_profiles
            [
                PairingProfile(
                    href='/orgs/1/pairing_profiles/19',
                    name='PP-DATABASE-VENS',
                    ...
                ),
                ...
            ]

        Returns:
            List[PairingProfile]: the returned list of decoded pairing profiles.
        """
        response = self.get('/pairing_profiles', **kwargs)
        return [PairingProfile.from_json(o) for o in response.json()]

    def create_pairing_profile(self, pairing_profile: PairingProfile, **kwargs) -> PairingProfile:
        """Creates a pairing profile object in the PCE.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#tocSpairing_profiles_post
        for details on POST body parameters when creating pairing profiles.

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

        Args:
            pairing_profile (PairingProfile): the pairing profile to create.

        Returns:
            PairingProfile: the re-encoded pairing profile object with valid HREF.
        """
        kwargs['json'] = pairing_profile.to_json()
        response = self.post('/pairing_profiles', **kwargs)
        return PairingProfile.from_json(response.json())

    def update_pairing_profile(self, href: str, pairing_profile: PairingProfile, **kwargs) -> None:
        """Updates a pairing profile object in the PCE.

        Usage:
            >>> from illumio.workloads import PairingProfile
            >>> pairing_profiles = pce.get_pairing_profiles(
            ...     params={'name': 'PP-DATABASE', 'max_results': 1}
            ... )
            >>> existing_profile = pairing_profiles[0]
            >>> update = PairingProfile(
            ...     name='PP-DATABASE-VENS',
            ...     enabled=False  # disable this profile
            ... )
            >>> updated_profile = pce.update_pairing_profile(existing_profile.href, update)
            >>> updated_profile
            PairingProfile(
                href='/orgs/1/pairing_profiles/19',
                name='PP-DATABASE-VENS',
                enabled=False,
                enforcement_mode='visibility_only',
                visibility_level='flows_summary',
                ...
            )

        Args:
            href (str): the HREF of the pairing profile to update.
            pairing_profile (PairingProfile): the updated pairing profile.
        """
        kwargs['json'] = pairing_profile.to_json()
        self.put(href, include_org=False, **kwargs)

    def delete_pairing_profile(self, href: str, **kwargs) -> None:
        """Deletes a pairing profile object in the PCE.

        Args:
            href (str): the HREF of the pairing profile to delete.
        """
        self.delete(href, include_org=False, **kwargs)

    def generate_pairing_key(self, pairing_profile_href: str, **kwargs) -> str:
        """Generates a pairing key using a pairing profile.

        Args:
            pairing_profile_href (str): the HREF of the pairing profile to use.

        Returns:
            str: the pairing key value.
        """
        uri = '{}/pairing_key'.format(pairing_profile_href)
        kwargs['json'] = {}
        response = self.post(uri, include_org=False, **kwargs)
        return response.json().get('activation_code')

    def get_workload(self, href: str, **kwargs) -> Workload:
        """Retrieves a workload from the PCE using its HREF.

        Args:
            href (str): the HREF of the workload object to fetch.

        Returns:
            Workload: the decoded workload object.
        """
        response = self.get(href, include_org=False, **kwargs)
        return Workload.from_json(response.json())

    def get_workloads(self, **kwargs) -> List[Workload]:
        """Retrieves workload objects from the PCE based on the given parameters.

        The Illumio APIs don't use pagination, opting instead for an async
        batch GET approach that can be slow. Instead, we accommodate large
        numbers of workloads by first fetching 0 results to get the
        X-Total-Count in the response, then fetching all results synchronously.
        This approach should have an advantage over an async call up to over
        100,000 workloads.

        If the `max_results` parameter is provided, this behaviour is overridden
        and the provided value is used instead.

        See https://docs.illumio.com/core/21.5/API-Reference/index.html#get-workloads
        for details on filter parameters for workload collection queries.

        Usage:
            >>> workloads = pce.get_workloads(
            ...     params={
            ...         'name': 'WIN-',
            ...         'managed': True
            ...     }
            ... )
            >>> workloads
            [
                Workload(
                    href='/orgs/1/workloads/6567900a-b49f-43cc-93a7-c892da39aad1',
                    name='WIN-JUMPBOX',
                    ...
                ),
                ...
            ]

        Returns:
            List[Workload]: the returned list of decoded workloads.
        """
        params = kwargs.get('params', {})

        if 'max_results' not in params:
            kwargs['params'] = {**params, **{'max_results': 0}}
            response = self.get('/workloads', **kwargs)
            filtered_workload_count = response.headers['X-Total-Count']
            kwargs['params'] = {**params, **{'max_results': int(filtered_workload_count)}}

        response = self.get('/workloads', **kwargs)
        return [Workload.from_json(o) for o in response.json()]

    def update_workload_enforcement_modes(self, enforcement_mode: EnforcementMode, workloads: List[Workload], **kwargs) -> dict:
        """Updates a list of workloads in the PCE to the provided enforcement mode.

        Args:
            enforcement_mode (EnforcementMode): the enforcement mode to change to.
            workloads (List[Workload]): list of workloads to update.

        Returns:
            dict: a dictionary containing a list of successfully updated
                workloads, as well as any errors returned from the PCE.
                Has the form {'workloads': [], 'errors': []}.
        """
        results = {'workloads': [], 'errors': []}
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
        """Retrieves Explorer traffic flows using the provided query.

        NOTE: this function is deprecated in the Illumio REST API, and is
        only provided for compatibility. The Illumio Explorer REST API
        documentation recommends using the async traffic flow query instead,
        provided here as `PolicyComputeEngine.get_traffic_flows_async`.

        See https://docs.illumio.com/core/21.5/Content/Guides/rest-api/visualization/explorer.htm#TrafficAnalysisQueries
        for details on traffic query parameters.

        Args:
            traffic_query (TrafficQuery): `TrafficQuery` object representing
                the query parameters.

        Returns:
            List[TrafficFlow]: list of `TrafficFlow` objects found using the
                provided query.
        """
        kwargs['json'] = traffic_query.to_json()
        response = self.post('/traffic_flows/traffic_analysis_queries', **kwargs)
        return [TrafficFlow.from_json(flow) for flow in response.json()]

    def get_traffic_flows_async(self, query_name: str, traffic_query: TrafficQuery, **kwargs) -> List[TrafficFlow]:
        """Retrieves Explorer traffic flows using the provided query.

        See https://docs.illumio.com/core/21.5/Content/Guides/rest-api/visualization/explorer.htm#AsynchronousQueriesforTrafficFlows
        for details on async traffic query parameters.

        Usage:
            >>> from illumio.explorer import TrafficQuery
            >>> traffic_query = TrafficQuery.build(
            ...     start_date="2022-02-01T00:00:00Z",
            ...     end_date="2022-03-01T00:00:00Z",
            ...     include_services=[
            ...         {'port': 3389, 'proto': 'tcp'}
            ...     ],
            ...     policy_decisions=['potentially_blocked', 'unknown']
            ... )
            >>> traffic_query
            TrafficQuery(
                start_date='2021-09-28T00:00:00Z',
                end_date='2021-10-05T00:00:00Z',
                sources=TrafficQueryFilterBlock(
                    include=[],
                    exclude=[]
                ),
                destinations=TrafficQueryFilterBlock(
                    include=[],
                    exclude=[]
                ),
                services=TrafficQueryServiceBlock(
                    include=[
                        ServicePort(
                            port=3389,
                            proto=6,
                            ...
                        )
                    ],
                    exclude=[]
                ),
                policy_decisions=[
                    'potentially_blocked',
                    'unknown'
                ],
                ...
            )
            >>> traffic_flows = pce.get_traffic_flows_async(
            ...     query_name='',
            ...     traffic_query=traffic_query
            ... )
            >>> traffic_flows
            [
                TrafficFlow(
                    src=TrafficNode(
                        ip='10.0.9.14',
                        "ip_lists": [
                            {
                                "name": "IPL-INTERNAL",
                                "href": "/orgs/1/sec_policy/active/ip_lists/5",
                                ...
                            }
                        ],
                        ...
                    ),
                    dst=TrafficNode(
                        ip='10.0.6.63',
                        workload=Workload(
                            href='/orgs/1/workloads/6567900a-b49f-43cc-93a7-c892da39aad1',
                            name='WIN-JUMPBOX',
                            ...
                        ),
                        ...
                    ),
                    service=ServicePort(port=3389, proto=6),
                    num_connections=44,
                    state='closed',
                    timestamp_range=TimestampRange(
                        first_detected='2022-02-19T09:50:17Z',
                        last_detected='2022-02-19T10:12:36Z'
                    ),
                    policy_decision='potentially_blocked',
                    flow_direction='inbound',
                    ...
                ),
                ...
            ]

        Args:
            query_name (str): name for the async query job.
            traffic_query (TrafficQuery): `TrafficQuery` object representing
                the query parameters.

        Raises:
            IllumioApiException: if there is an error retrieving the async job
                results.

        Returns:
            List[TrafficFlow]: list of `TrafficFlow` objects found using the
                provided query.
        """
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
        """Provisions policy changes for draft objects with the given HREFs.

        Usage:
            >>> from illumio.rules import Ruleset
            >>> ruleset = pce.create_ruleset(
            ...     Ruleset(name='RS-RINGFENCE')
            ... )
            >>> changeset = pce.provision_policy_changes(
            ...     change_description='Provision ring-fence ruleset',
            ...     hrefs=[ruleset.href]
            ... )
            >>> changeset
            PolicyVersion(
                href='/orgs/1/sec_policy/110',
                commit_message='Provision ring-fence ruleset',
                version=110,
                workloads_affected=0,
                object_counts=PolicyObjectCounts(
                    label_groups=17,
                    services=8,
                    ...
                )
            )

        Args:
            change_description (str): the policy change description.
            hrefs (List[str]): the HREFs of the draft policy objects to provision.

        Raises:
            IllumioException: if an invalid HREF is provided.

        Returns:
            PolicyVersion: the decoded policy version object including the
                changeset.
        """
        policy_changeset = PolicyChangeset.build(hrefs)
        kwargs['json'] = {'update_description': change_description, 'change_subset': policy_changeset.to_json()}
        response = self.post('/sec_policy', **kwargs)
        return PolicyVersion.from_json(response.json())


__all__ = ['PolicyComputeEngine']
