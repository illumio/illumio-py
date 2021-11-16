import json
import os
import re

import pytest
from requests_mock import ANY

from illumio import IllumioException
from illumio.util import IllumioEncoder
from illumio.policyobjects import VirtualService, ServicePort, ServiceAddress, Label

MOCK_VIRTUAL_SERVICE = os.path.join(pytest.DATA_DIR, 'virtual_service.json')


@pytest.fixture(scope='module')
def mock_virtual_service() -> VirtualService:
    with open(MOCK_VIRTUAL_SERVICE, 'r') as f:
        yield VirtualService.from_json(f.read())


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_virtual_service):
    matcher = re.compile('/sec_policy/draft/virtual_services')
    requests_mock.register_uri(ANY, matcher, json=json.dumps(mock_virtual_service, cls=IllumioEncoder))


def test_decoded_service_ports(mock_virtual_service):
    assert type(mock_virtual_service.service_ports[0]) is ServicePort


def test_decoded_service_addresses(mock_virtual_service):
    assert type(mock_virtual_service.service_addresses[0]) is ServiceAddress


def test_decoded_labels(mock_virtual_service):
    assert type(mock_virtual_service.labels[0]) is Label


def test_get_virtual_service(pce, mock_virtual_service):
    virtual_service = pce.get_virtual_service(mock_virtual_service.href)
    assert virtual_service.name == 'test-service'


def test_create_virtual_service(pce, mock_virtual_service):
    created_virtual_service = pce.create_virtual_service(mock_virtual_service)
    assert created_virtual_service.name == 'test-service'


def test_invalid_apply_to_value():
    with pytest.raises(IllumioException):
        VirtualService(href='/test/href', name='VS-TEST', apply_to='invalid_value')
