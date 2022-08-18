import json
import os
import re
from typing import List

import pytest

from illumio import IllumioException
from illumio.policyobjects import IPList, IPRange
from illumio.util import ANY_IP_LIST_NAME, DRAFT, ACTIVE

IP_LISTS = os.path.join(pytest.DATA_DIR, 'ip_lists.json')


@pytest.fixture(scope='module')
def ip_lists() -> List[dict]:
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


@pytest.fixture(autouse=True)
def ip_lists_mock(pce_object_mock, ip_lists):
    pce_object_mock.add_mock_objects(ip_lists)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/sec_policy/(draft|active)/ip_lists')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


def test_get_default_ip_list(pce):
    default_ip_list = pce.get_default_ip_list()
    assert default_ip_list.name == ANY_IP_LIST_NAME


def test_get_by_reference(pce):
    any_ip_list = pce.ip_lists.get_by_reference('/orgs/1/sec_policy/active/ip_lists/1')
    assert any_ip_list.name == ANY_IP_LIST_NAME


def test_get_by_name(pce):
    ip_lists = pce.ip_lists.get(params={"name": "IPL-"}, policy_version=DRAFT)
    repeated_ip_lists = [ip_list for ip_list in ip_lists if ip_list.name == "IPL-4"]
    assert len(repeated_ip_lists) == 1
    assert '/draft/' in repeated_ip_lists[0].href


def test_get_active_ip_list(pce):
    ip_lists = pce.ip_lists.get(params={"name": "IPL-"}, policy_version=ACTIVE)
    repeated_ip_lists = [ip_list for ip_list in ip_lists if ip_list.name == "IPL-4"]
    assert len(repeated_ip_lists) == 1
    assert '/active/' in repeated_ip_lists[0].href


def test_create_ip_list(pce, new_ip_list):
    ip_list = pce.ip_lists.create(new_ip_list)
    assert ip_list.href != ''
    fetched_ip_list = pce.ip_lists.get_by_reference(ip_list.href)
    assert fetched_ip_list == ip_list


def test_update_ip_list(pce):
    ip_list = pce.ip_lists.get(params={"name": "IPL-4", 'max_results': 1})[0]
    pce.ip_lists.update(ip_list.href, {'fqdns': [{'fqdn': 'test.example.com'}]})
    updated_ip_list = pce.ip_lists.get_by_reference(ip_list.href)
    assert len(updated_ip_list.fqdns) > 0
    assert updated_ip_list.fqdns[0].fqdn == 'test.example.com'


def test_valid_ip_ranges():
    IPRange(from_ip='10.0.0.0', to_ip='10.0.0.1')
    IPRange(from_ip='10.0.0.0/8')
    IPRange(from_ip='10.0.0.0/32')
    IPRange(from_ip='10.0.0.0/32', to_ip='10.0.0.1')


def test_validate_ip_range_to_ip_passed_with_from_ip_cidr():
    with pytest.raises(IllumioException):
        IPRange(from_ip='10.0.0.0/8', to_ip='11.0.0.0')


def test_validate_ip_range_lower_to_ip():
    with pytest.raises(IllumioException):
        IPRange(from_ip='10.0.0.1', to_ip='10.0.0.0')


def test_validate_ip_range_to_ip_cidr():
    with pytest.raises(IllumioException):
        IPRange(from_ip='10.0.0.0', to_ip='11.0.0.0/8')
