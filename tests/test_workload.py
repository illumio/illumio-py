import json
import os
import re

import pytest

from illumio.policyobjects import Service, ServicePort
from illumio.workloads import Workload

MOCK_WORKLOAD = os.path.join(pytest.DATA_DIR, 'workload.json')


@pytest.fixture(scope='module')
def mock_workload() -> dict:
    with open(MOCK_WORKLOAD, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_workload):
    matcher = re.compile('/workloads')
    requests_mock.register_uri(
        'GET', matcher,
        headers={"X-Total-Count": "1"},
        json=[mock_workload]
    )


def test_decoding(mock_workload):
    workload = Workload.from_json(mock_workload)
    assert isinstance(workload, Workload)


def test_selectively_enforced_services(mock_workload):
    workload = Workload.from_json(mock_workload)
    assert len(workload.selectively_enforced_services) == 4
    assert isinstance(workload.selectively_enforced_services[0], Service) \
        and isinstance(workload.selectively_enforced_services[2], ServicePort)


def test_get_by_enforcement_mode(pce):
    workloads = pce.get_workloads(params={
        "enforcement_mode": "visibility_only"
    })
    assert len(workloads) == 1
