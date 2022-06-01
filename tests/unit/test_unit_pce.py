import json
import os
import re

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


def load_data_file(type_):
    filename = os.path.join(pytest.DATA_DIR, '{}.json'.format(type_))
    with open(filename, 'r') as f:
        return json.loads(f.read())


@pytest.mark.parametrize(
    "api_name,endpoint,cls,is_sec_policy",
    [
        (name, api_args[0], api_args[1], api_args[2])
        for name, api_args in PCE_APIS.items()
    ]
)
def test_pce_apis(api_name, endpoint, cls, is_sec_policy, pce, requests_mock,
        get_callback, post_callback, put_callback, delete_callback):
    api = getattr(pce, api_name)

    pattern = re.compile(endpoint)
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)

    obj = api.create(cls(name='test object'))
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
