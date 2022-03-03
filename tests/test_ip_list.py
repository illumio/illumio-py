import json
import os
import re

import pytest
from requests_mock import ANY

from illumio import PolicyComputeEngine, IllumioException
from illumio.util import IllumioEncoder, ANY_IP_LIST_NAME
from illumio.policyobjects import IPList

DRAFT_IP_LISTS = os.path.join(pytest.DATA_DIR, 'draft_ip_lists.json')
ACTIVE_IP_LISTS = os.path.join(pytest.DATA_DIR, 'active_ip_lists.json')


@pytest.fixture(scope='module')
def draft_ip_lists() -> IPList:
    with open(DRAFT_IP_LISTS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def active_ip_lists() -> IPList:
    with open(ACTIVE_IP_LISTS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, draft_ip_lists, active_ip_lists):
    draft_matcher = re.compile('/sec_policy/draft/ip_lists')
    requests_mock.register_uri(ANY, draft_matcher, json=draft_ip_lists)
    active_matcher = re.compile('/sec_policy/active/ip_lists')
    requests_mock.register_uri(ANY, active_matcher, json=active_ip_lists)


def test_get_default_ip_list(pce: PolicyComputeEngine):
    default_ip_list = pce.get_default_ip_list()
    assert default_ip_list.name == ANY_IP_LIST_NAME


def test_active_overrides_draft(pce: PolicyComputeEngine):
    ip_lists = pce.get_ip_lists(params={"name": "IPL-"})
    repeated_ip_lists = [ip_list for ip_list in ip_lists if ip_list.name == "IPL-4"]
    assert len(repeated_ip_lists) == 1
    assert '/active/' in repeated_ip_lists[0].href
