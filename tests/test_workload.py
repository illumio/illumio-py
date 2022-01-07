import json
import os
import re

import pytest
from requests_mock import ANY

from illumio.policyobjects import Service, ServicePort
from illumio.util import IllumioEncoder
from illumio.workloads import Workload

MOCK_WORKLOAD = os.path.join(pytest.DATA_DIR, 'workload.json')


@pytest.fixture(scope='module')
def mock_workload() -> Workload:
    with open(MOCK_WORKLOAD, 'r') as f:
        yield Workload.from_json(f.read())


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_workload):
    matcher = re.compile('/workloads')
    requests_mock.register_uri(ANY, matcher, json=json.dumps(mock_workload, cls=IllumioEncoder))


def test_decoding(mock_workload):
    assert isinstance(mock_workload, Workload)


def test_selectively_enforced_services(mock_workload):
    assert len(mock_workload.selectively_enforced_services) == 4
    assert isinstance(mock_workload.selectively_enforced_services[0], Service) \
        and isinstance(mock_workload.selectively_enforced_services[2], ServicePort)
