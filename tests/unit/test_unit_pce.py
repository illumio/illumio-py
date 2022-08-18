import re
from collections import namedtuple
from dataclasses import fields

import pytest

from illumio import PolicyComputeEngine
from illumio.accessmanagement import User
from illumio.exceptions import IllumioIntegerValidationException
from illumio.infrastructure import ContainerWorkloadProfile
from illumio.policyobjects import Label
from illumio.rules import Rule
from illumio.util import PCE_APIS, DRAFT, ACTIVE

from mocks import MockResponse


def test_custom_protocol():
    pce = PolicyComputeEngine('http://my.pce.com')
    assert pce.base_url == 'http://my.pce.com:443/api/v2'


def test_invalid_protocol():
    pce = PolicyComputeEngine('ftp://my.pce.com')
    assert pce.base_url == 'https://my.pce.com:443/api/v2'


def test_protocol_parsing():
    pce = PolicyComputeEngine('httpslab.pce.com')
    assert pce.base_url == 'https://httpslab.pce.com:443/api/v2'


def test_path_parsing():
    pce = PolicyComputeEngine('my.pce.com/api/v2')
    assert pce.base_url == 'https://my.pce.com:443/api/v2'


def test_int_org_id():
    pce = PolicyComputeEngine('my.pce.com', org_id=1)
    assert pce.base_url == 'https://my.pce.com:443/api/v2'


def test_invalid_org_id():
    with pytest.raises(IllumioIntegerValidationException):
        PolicyComputeEngine('my.pce.com', org_id='invalid')


def test_org_id_lower_bound():
    with pytest.raises(IllumioIntegerValidationException):
        PolicyComputeEngine('my.pce.com', org_id=0)


def test_invalid_port():
    with pytest.raises(IllumioIntegerValidationException):
        PolicyComputeEngine('my.pce.com', port='invalid')


def test_port_lower_bound():
    with pytest.raises(IllumioIntegerValidationException):
        PolicyComputeEngine('my.pce.com', port=-1)


def test_port_upper_bound():
    with pytest.raises(IllumioIntegerValidationException):
        PolicyComputeEngine('my.pce.com', port=65536)


_API = namedtuple('API', [
    'name',
    'endpoint',
    'object_class',
    'is_sec_policy',
    'is_global'
])


@pytest.fixture(autouse=True)
def mock_requests(requests_mock):
    pattern = re.compile('/')
    requests_mock.register_uri('GET', pattern)
    requests_mock.register_uri('POST', pattern, status_code=201)
    requests_mock.register_uri('PUT', pattern, status_code=204)
    requests_mock.register_uri('DELETE', pattern, status_code=204)


@pytest.mark.parametrize(
    "api,policy_version,parent,expected", [
        (
            _API(name='users', endpoint='/users', object_class=User, is_sec_policy=False, is_global=True),
            None, None, '/users'
        ),
        (
            _API(name='labels', endpoint='/labels', object_class=Label, is_sec_policy=False, is_global=False),
            None, None, '/orgs/1/labels'
        ),
        (
            _API(name='rules', endpoint='/sec_rules', object_class=Rule, is_sec_policy=True, is_global=False),
            DRAFT, '/orgs/1/sec_policy/active/rule_sets/1', '/orgs/1/sec_policy/draft/rule_sets/1/sec_rules'
        ),
        (
            _API(name='rules', endpoint='/sec_rules', object_class=Rule, is_sec_policy=True, is_global=False),
            ACTIVE, '/orgs/1/sec_policy/active/rule_sets/1', '/orgs/1/sec_policy/draft/rule_sets/1/sec_rules'
        ),
        (
            _API(name='container_workload_profiles', endpoint='/container_workload_profiles', object_class=ContainerWorkloadProfile, is_sec_policy=False, is_global=False),
            ACTIVE, '/orgs/1/container_clusters/f5bef182-8c55-4219-b35b-0a50b707e434', '/orgs/1/container_clusters/f5bef182-8c55-4219-b35b-0a50b707e434/container_workload_profiles'
        )
    ]
)
def test_endpoint_building(api, policy_version, parent, expected, pce):
    endpoint = PolicyComputeEngine._PCEObjectAPI(pce, api)._build_endpoint(policy_version, parent)
    assert endpoint == expected


@pytest.fixture
def called_with():
    class Tester(object):
        def __call__(self, *args, **kwargs):
            self.args = list(args)
            return MockResponse()
    return Tester()


@pytest.mark.parametrize(
    "api_name,expected", [
        ('users', 'https://test.pce.com:443/api/v2/users'),
        ('labels', 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('ip_lists', 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/draft/ip_lists')
    ]
)
def test_internal_api_org_inclusion(api_name, expected, monkeypatch, called_with):
    monkeypatch.setattr("requests.sessions.Session.request", called_with)
    pce = PolicyComputeEngine('test.pce.com')
    api = getattr(pce, api_name)
    api.get(include_org=True)
    assert called_with.args == ['GET', expected]
    api.get_all(include_org=True)
    assert called_with.args == ['GET', expected]
    api.create({}, include_org=True)
    assert called_with.args == ['POST', expected]



@pytest.mark.parametrize(
    "api_name,href,expected", [
        ('users', '/users/1', 'https://test.pce.com:443/api/v2/users/1'),
        ('labels', '/orgs/1/labels/1', 'https://test.pce.com:443/api/v2/orgs/1/labels/1'),
        ('ip_lists', '/orgs/1/sec_policy/draft/ip_lists/1', 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/draft/ip_lists/1')
    ]
)
def test_internal_api_org_inclusion_with_href(api_name, href, expected, monkeypatch, called_with):
    monkeypatch.setattr("requests.sessions.Session.request", called_with)
    pce = PolicyComputeEngine('test.pce.com')
    api = getattr(pce, api_name)
    api.get_by_reference(href, include_org=True)
    assert called_with.args == ['GET', expected]
    api.update(href, {}, include_org=True)
    assert called_with.args == ['PUT', expected]
    api.delete(href, include_org=True)
    assert called_with.args == ['DELETE', expected]


@pytest.mark.parametrize(
    "endpoint,include_org,expected", [
        ('/health', False, 'https://test.pce.com:443/api/v2/health'),
        ('labels', True, 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('/labels', True, 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('//labels', True, 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('/sec_policy/active//ip_lists', True, 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/active/ip_lists'),
        ('/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53', True, 'https://test.pce.com:443/api/v2/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53'),
        ('/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53', False, 'https://test.pce.com:443/api/v2/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53'),
        ('/orgs/1/sec_policy/rule_sets/1/sec_rules/1', True, 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/rule_sets/1/sec_rules/1')
    ]
)
def test_url_building(endpoint, include_org, expected, pce):
    assert pce._build_url(endpoint, include_org) == expected


@pytest.mark.parametrize(
    "endpoint,expected", [
        ('/health', 'https://test.pce.com:443/api/v2/health'),
        ('/labels', 'https://test.pce.com:443/api/v2/labels'),
        ('/sec_policy/active//ip_lists', 'https://test.pce.com:443/api/v2/sec_policy/active/ip_lists'),
        ('/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53', 'https://test.pce.com:443/api/v2/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53'),
        ('/orgs/1/sec_policy/rule_sets/1/sec_rules/1', 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/rule_sets/1/sec_rules/1')
    ]
)
def test_set_include_org_default(endpoint, expected):
    pce = PolicyComputeEngine('test.pce.com')
    pce.include_org = False
    response = pce.get(endpoint)
    assert response.url == expected


def test_ignore_include_org(pce):
    assert pce.check_connection(include_org=True)


@pytest.mark.parametrize(
    "api_name,endpoint,ObjectClass,is_sec_policy",
    [
        (name, api.endpoint, api.object_class, api.is_sec_policy)
        for name, api in PCE_APIS.items()
    ]
)
def test_pce_apis(api_name, endpoint, ObjectClass, is_sec_policy, pce,
        requests_mock, get_callback, post_callback, put_callback, delete_callback):
    api = getattr(pce, api_name)

    pattern = re.compile(endpoint)
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)

    params = {}
    if 'name' in [field.name for field in fields(ObjectClass)]:
        params = {'name': 'test object'}

    obj = api.create(ObjectClass(**params))
    assert obj.href

    policy_version = DRAFT if is_sec_policy else None
    assert api.get_by_reference(obj.href) == obj

    if params:
        objs = api.get(params=params, policy_version=policy_version)
        assert objs[0] == obj

    api.update(obj.href, {'description': 'updated description'})
    obj = api.get_by_reference(obj.href)
    assert obj.description == 'updated description'

    api.delete(obj.href)
    objs = api.get(policy_version=policy_version)
    assert len(objs) == 0
