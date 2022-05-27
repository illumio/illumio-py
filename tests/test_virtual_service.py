import json
import os
import re

import pytest

from illumio import PolicyComputeEngine, IllumioException
from illumio.policyobjects import VirtualService, ServicePort, ServiceAddress, Label

VIRTUAL_SERVICES = os.path.join(pytest.DATA_DIR, 'virtual_services.json')


@pytest.fixture(scope='module')
def virtual_services() -> list:
    with open(VIRTUAL_SERVICES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def new_service() -> VirtualService:
    return VirtualService(
        name="VS-TEST",
        service_ports=[
            ServicePort(port=443, proto="TCP")
        ]
    )


@pytest.fixture(scope='module')
def virtual_services_mock(PolicyObjectMock, virtual_services):
    yield PolicyObjectMock(virtual_services)


@pytest.fixture(scope='module')
def get_callback(virtual_services_mock):
    def _callback_fn(request, context):
        return virtual_services_mock.get_mock_objects(request.path_url)
    return _callback_fn


@pytest.fixture(scope='module')
def post_callback(new_service):
    def _callback_fn(request, context):
        return new_service.to_json()
    return _callback_fn


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback):
    pattern = re.compile('/sec_policy/(draft|active)/virtual_services')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)


@pytest.fixture()
def mock_virtual_service(pce: PolicyComputeEngine):
    yield pce.get_virtual_service("/orgs/1/sec_policy/draft/virtual_services/14d7ff69-2fa4-458b-a299-e3f11ffa9b01")


def test_decoded_service_ports(mock_virtual_service: VirtualService):
    assert type(mock_virtual_service.service_ports[0]) is ServicePort


def test_decoded_service_addresses(mock_virtual_service: VirtualService):
    assert type(mock_virtual_service.service_addresses[0]) is ServiceAddress


def test_decoded_labels(mock_virtual_service: VirtualService):
    assert type(mock_virtual_service.labels[0]) is Label


def test_create_virtual_service(pce: PolicyComputeEngine, new_service: VirtualService):
    created_virtual_service = pce.create_virtual_service(new_service)
    assert created_virtual_service.name == 'VS-TEST'


def test_invalid_protocol_name():
    with pytest.raises(IllumioException):
        VirtualService(
            name='VS-TEST', service_ports=[
                ServicePort(port=443, proto="invalidproto")
            ]
        )


def test_invalid_apply_to_value():
    with pytest.raises(IllumioException):
        VirtualService(href='/test/href', name='VS-TEST', apply_to='invalid_value')


def test_get_by_name_deprecation(pce: PolicyComputeEngine):
    with pytest.deprecated_call():
        pce.get_virtual_services_by_name(name="VS-TEST")
