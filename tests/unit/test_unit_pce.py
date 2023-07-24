import os
import re
from collections import namedtuple
from contextlib import suppress as does_not_raise
from dataclasses import fields

import pytest
from requests_mock import ANY

from illumio import PolicyComputeEngine
from illumio.accessmanagement import User
from illumio.exceptions import (
    IllumioApiException,
    IllumioIntegerValidationException,
)
from illumio.infrastructure import ContainerWorkloadProfile
from illumio.policyobjects import Label
from illumio.rules import Rule
from illumio.util import PCE_APIS, DRAFT, ACTIVE

from mocks import MockResponse

TLS_DIR = os.path.join(pytest.DATA_DIR, 'tls')


@pytest.mark.parametrize(
    "url,expected_base_url", [
        ("http://my.pce.com", "http://my.pce.com:443/api/v2"),
        ("ftp://my.pce.com", "https://my.pce.com:443/api/v2"),
        ("httpslab.pce.com", "https://httpslab.pce.com:443/api/v2"),
        ("my.pce.com/api/v2", "https://my.pce.com:443/api/v2"),
    ]
)
def test_url_parsing(url, expected_base_url):
    pce = PolicyComputeEngine(url)
    assert pce.base_url == expected_base_url


@pytest.mark.parametrize(
    "org_id,expected", [
        (1, does_not_raise()),
        ("1", does_not_raise()),
        ("invalid", pytest.raises(IllumioIntegerValidationException)),
        (0, pytest.raises(IllumioIntegerValidationException)),
    ]
)
def test_org_id_values(org_id, expected):
    with expected:
        PolicyComputeEngine('my.pce.com', org_id=org_id)


@pytest.mark.parametrize(
    "port,expected", [
        (443, does_not_raise()),
        (65535, does_not_raise()),
        ("invalid", pytest.raises(IllumioIntegerValidationException)),
        (-1, pytest.raises(IllumioIntegerValidationException)),
        (65536, pytest.raises(IllumioIntegerValidationException)),
    ]
)
def test_port_values(port, expected):
    with expected:
        PolicyComputeEngine('my.pce.com', port=port)


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
    "verify,cert",
    [
        (True, None),
        (False, None),
        (os.path.join(TLS_DIR, "rootca"), None),
        (True, os.path.join(TLS_DIR, "client.pem")),
        (True, (os.path.join(TLS_DIR, "client.crt"), os.path.join(TLS_DIR, "client.key")))
    ]
)
def test_tls_settings(verify, cert, pce):
    pce.set_tls_settings(verify=verify, cert=cert)
    assert pce.check_connection()


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


@pytest.mark.parametrize(
    "status_code,error_resp,messages", [
        (410, 410, ["410"]),
        (
            400,
            [{"token": "invalid_argument", "message": "No such argument: 'foo'"}],
            ["invalid_argument: No such argument: 'foo'"]
        ),
        (
            500,
            [{"error": "server error"}, {"error": "server busy"}],
            ["server error", "server busy"]
        ),
        (
            500,
            [{"exception": "server error"}],
            ["{'exception': 'server error'}"]
        ),
    ]
)
def test_error_handling(status_code, error_resp, messages, requests_mock, pce):
    requests_mock.register_uri(
        ANY, ANY,
        status_code=status_code, json=error_resp,
        headers={"Content-Type": "application/json"}
    )

    with pytest.raises(IllumioApiException) as exc_info:
        pce.labels.get()

    for message in messages:
        assert message in str(exc_info.value)


@pytest.mark.parametrize(
    "objs,responses,expected_results", [
        (
            [
                {
                    "href": "/orgs/1/workloads/e84e57ff-39ee-475d-9e20-4ec6734b48ec"
                },
                {
                    "href": "/orgs/1/workloads/f0a18d81-6bc3-41f5-86ad-e395919a73e5"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/e84e57ff-39ee-475d-9e20-4ec6734b48ec",
                    "status": "updated"
                },
                {
                    "href": "/orgs/1/workloads/f0a18d81-6bc3-41f5-86ad-e395919a73e5",
                    "status": "updated"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/e84e57ff-39ee-475d-9e20-4ec6734b48ec",
                    "errors": []
                },
                {
                    "href": "/orgs/1/workloads/f0a18d81-6bc3-41f5-86ad-e395919a73e5",
                    "errors": []
                },
            ]
        ),
        (
            [
                {
                    "href": "/orgs/1/workloads/43f93186-b415-4934-aaf6-e8206ff1f12c"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/43f93186-b415-4934-aaf6-e8206ff1f12c",
                    "status": "failed",
                    "token": "invalid_uri",
                    "message": "Invalid URI: {/orgs/1/workloads/43f93186-b415-4934-aaf6-e8206ff1f12c}"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/43f93186-b415-4934-aaf6-e8206ff1f12c",
                    "errors": [
                        {
                            "token": "invalid_uri",
                            "message": "Invalid URI: {/orgs/1/workloads/43f93186-b415-4934-aaf6-e8206ff1f12c}"
                        }
                    ]
                }
            ]
        ),
        (
            [
                {
                    "href": "/orgs/1/workloads/27920c5b-8b27-423e-bda8-83ec955a2e13"
                },
                {
                    "href": "/orgs/1/workloads/b35ea3f2-458f-42f3-b2d5-957e771c1cfc"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/27920c5b-8b27-423e-bda8-83ec955a2e13",
                    "status": "failed",
                    "error": "server_error"
                },
                {
                    "error": "server_error"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/27920c5b-8b27-423e-bda8-83ec955a2e13",
                    "errors": [
                        {
                            "token": "bulk_change_error",
                            "message": "{\"href\": \"/orgs/1/workloads/27920c5b-8b27-423e-bda8-83ec955a2e13\", \"status\": \"failed\", \"error\": \"server_error\"}"
                        }
                    ]
                },
                {
                    "href": None,
                    "errors": [{"token": "bulk_change_error", "message": "{\"error\": \"server_error\"}"}]
                }
            ]
        ),
        (
            [
                {
                    "href": "/orgs/1/workloads/1313d3f8-3ecd-44b2-adfe-bf23f5752513"
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/1313d3f8-3ecd-44b2-adfe-bf23f5752513",
                    "status": "failed",
                    "errors": [
                        {
                            "token": "method_not_allowed_error",
                            "message": "Not allowed"
                        },
                        {
                            "token": "not_found_error",
                            "message": "Not found"
                        }
                    ]
                }
            ],
            [
                {
                    "href": "/orgs/1/workloads/1313d3f8-3ecd-44b2-adfe-bf23f5752513",
                    "errors": [
                        {
                            "token": "method_not_allowed_error",
                            "message": "Not allowed"
                        },
                        {
                            "token": "not_found_error",
                            "message": "Not found"
                        }
                    ]
                }
            ]
        ),
    ]
)
def test_bulk_error_handling(objs, responses, expected_results, requests_mock, pce):
    requests_mock.register_uri(
        ANY, ANY, json=responses,
        headers={"Content-Type": "application/json"}
    )

    results = pce.workloads.bulk_update(objs)
    assert results == expected_results
