import json
import os
import re
from this import d

import pytest

from illumio import PolicyComputeEngine
from illumio.util import PCE_APIS, DRAFT


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


@pytest.mark.parametrize(
    "endpoint,include_org,expected", [
        ('/health', False, 'https://test.pce.com:443/api/v2/health'),
        ('labels', True, 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('/labels', True, 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('//labels', True, 'https://test.pce.com:443/api/v2/orgs/1/labels'),
        ('/sec_policy/active//ip_lists', True, 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/active/ip_lists'),
        ('/sec_policy/active//ip_lists', True, 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/active/ip_lists'),
        ('/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53', True, 'https://test.pce.com:443/api/v2/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53'),
        ('/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53', False, 'https://test.pce.com:443/api/v2/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53'),
        ('/orgs/1/sec_policy/rule_sets/1/sec_rules/1', True, 'https://test.pce.com:443/api/v2/orgs/1/sec_policy/rule_sets/1/sec_rules/1')
    ]
)
def test_url_building(endpoint, include_org, expected, pce):
    assert pce._build_url(endpoint, include_org) == expected


def load_data_file(type_):
    filename = os.path.join(pytest.DATA_DIR, '{}.json'.format(type_))
    with open(filename, 'r') as f:
        return json.loads(f.read())


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

    obj = api.create(ObjectClass(name='test object'))
    assert obj.href

    policy_version = DRAFT if is_sec_policy else None
    assert api.get_by_href(obj.href) == obj

    objs = api.get(params={'name': 'test object'}, policy_version=policy_version)
    assert objs[0] == obj

    api.update(obj.href, {'description': 'updated description'})
    obj = api.get_by_href(obj.href)
    assert obj.description == 'updated description'

    api.delete(obj.href)
    objs = api.get(policy_version=policy_version)
    assert len(objs) == 0
