import json
import os
import re

import pytest

from illumio import PolicyComputeEngine
from illumio.policyobjects import IPList, IPRange
from illumio.util import ANY_IP_LIST_NAME

IP_LISTS = os.path.join(pytest.DATA_DIR, 'ip_lists.json')


@pytest.fixture(scope='module')
def ip_lists() -> list:
    with open(IP_LISTS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def new_ip_list() -> IPList:
    return IPList(
        name="IPL-INTERNAL",
        ip_ranges=[
            IPRange(from_ip='10.0.0.0/8'),
            IPRange(from_ip='172.16.0.0/12'),
            IPRange(from_ip='192.168.0.0', to_ip='192.168.255.255')
        ]
    )


@pytest.fixture(scope='module')
def ip_lists_mock(PolicyObjectMock, ip_lists):
    yield PolicyObjectMock(ip_lists)


@pytest.fixture(scope='module')
def get_callback(ip_lists_mock):
    def _callback_fn(request, context):
        return ip_lists_mock.get_mock_objects(request.path_url)
    return _callback_fn


@pytest.fixture(scope='module')
def post_callback(new_ip_list):
    def _callback_fn(request, context):
        return new_ip_list.to_json()
    return _callback_fn


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback):
    pattern = re.compile('/sec_policy/(draft|active)/ip_lists')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)


def test_get_default_ip_list(pce: PolicyComputeEngine):
    default_ip_list = pce.get_default_ip_list()
    assert default_ip_list.name == ANY_IP_LIST_NAME


def test_active_overrides_draft(pce: PolicyComputeEngine):
    ip_lists = pce.get_ip_lists(params={"name": "IPL-"})
    repeated_ip_lists = [ip_list for ip_list in ip_lists if ip_list.name == "IPL-4"]
    assert len(repeated_ip_lists) == 1
    assert '/active/' in repeated_ip_lists[0].href


def test_get_by_name(pce: PolicyComputeEngine):
    ip_lists = pce.get_ip_lists_by_name(name="IPL-")
    assert len(ip_lists) == 3


def test_get_by_name_deprecation(pce: PolicyComputeEngine):
    with pytest.deprecated_call():
        pce.get_ip_lists_by_name(name="TEST")
