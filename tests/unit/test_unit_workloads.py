import json
import os
import re
from typing import List

import pytest

from illumio.policyobjects import Service, ServicePort
from illumio.util import EnforcementMode
from illumio.workloads import Workload

MOCK_WORKLOADS = os.path.join(pytest.DATA_DIR, 'workloads.json')


@pytest.fixture(scope='module')
def workloads() -> List[dict]:
    with open(MOCK_WORKLOADS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def new_workload() -> Workload:
    return Workload(
        name='db0.internal.labs.io',
        hostname='db0.internal.labs.io'
    )


@pytest.fixture(autouse=True)
def workloads_mock(pce_object_mock, workloads):
    pce_object_mock.add_mock_objects(workloads)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    profile_pattern = re.compile('/workloads')
    requests_mock.register_uri('GET', profile_pattern, json=get_callback)
    requests_mock.register_uri('POST', profile_pattern, json=post_callback)
    requests_mock.register_uri('PUT', profile_pattern, json=put_callback)
    requests_mock.register_uri('DELETE', profile_pattern, json=delete_callback)


@pytest.fixture()
def mock_workload(pce):
    yield pce.workloads.get_by_reference("/orgs/1/workloads/ef7f0f53-2295-4416-aaaf-965146934c53")


def test_pass_enforcement_mode_as_enum():
    workload = Workload(name='test workload', enforcement_mode=EnforcementMode.VISIBILITY_ONLY)
    assert workload.enforcement_mode in EnforcementMode


def test_selectively_enforced_services(mock_workload):
    assert len(mock_workload.selectively_enforced_services) == 4
    assert isinstance(mock_workload.selectively_enforced_services[0], Service) \
        and isinstance(mock_workload.selectively_enforced_services[2], ServicePort)


def test_get_by_enforcement_mode(pce):
    workloads = pce.workloads.get(params={'enforcement_mode': 'visibility_only'})
    assert len(workloads) == 1


def test_create_workload(pce, new_workload):
    created_workload = pce.workloads.create(new_workload)
    assert created_workload.href != ''
    workload = pce.workloads.get_by_reference(created_workload.href)
    assert created_workload == workload


def test_update_workload(pce, mock_workload):
    pce.workloads.update(mock_workload.href, {'enforcement_mode': 'selective'})
    updated_workload = pce.workloads.get_by_reference(mock_workload.href)
    assert updated_workload.enforcement_mode == 'selective'
