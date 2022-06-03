import json
import os
import re
from typing import List

import pytest

from illumio import IllumioException
from illumio.policyobjects import VirtualService, ServicePort, ServiceAddress
from illumio.util import Reference, DRAFT

VIRTUAL_SERVICES = os.path.join(pytest.DATA_DIR, 'virtual_services.json')


@pytest.fixture(scope='module')
def virtual_services() -> List[dict]:
    with open(VIRTUAL_SERVICES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def new_virtual_service() -> VirtualService:
    return VirtualService(
        name="VS-TEST",
        service_ports=[
            ServicePort(port=443, proto="TCP")
        ]
    )


@pytest.fixture(autouse=True)
def virtual_services_mock(pce_object_mock, virtual_services):
    pce_object_mock.add_mock_objects(virtual_services)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/sec_policy/(draft|active)/virtual_services')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


@pytest.fixture()
def mock_virtual_service(pce):
    yield pce.virtual_services.get_by_reference("/orgs/1/sec_policy/draft/virtual_services/14d7ff69-2fa4-458b-a299-e3f11ffa9b01")


def test_decoded_service_ports(mock_virtual_service: VirtualService):
    assert type(mock_virtual_service.service_ports[0]) is ServicePort


def test_decoded_service_addresses(mock_virtual_service: VirtualService):
    assert type(mock_virtual_service.service_addresses[0]) is ServiceAddress


def test_decoded_labels(mock_virtual_service: VirtualService):
    assert type(mock_virtual_service.labels[0]) is Reference


def test_create_virtual_service(pce, new_virtual_service: VirtualService):
    created_virtual_service = pce.create_virtual_service(new_virtual_service)
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


def test_get_by_name(pce):
    virtual_services = pce.virtual_services.get(params={'name': 'VS-'})
    assert len(virtual_services) == 1


def test_get_draft_virtual_services(pce, mock_virtual_service):
    virtual_service = pce.virtual_services.get(params={'name': 'VS-INTERNAL', 'max_results': 1}, policy_version=DRAFT)[0]
    assert virtual_service == mock_virtual_service


def test_create_virtual_service(pce, new_virtual_service):
    created_virtual_service = pce.virtual_services.create(new_virtual_service)
    assert created_virtual_service.href != ''
    virtual_service = pce.virtual_services.get_by_reference(created_virtual_service.href)
    assert created_virtual_service == virtual_service


def test_update_virtual_service(pce, mock_virtual_service):
    pce.virtual_services.update(mock_virtual_service.href, {'enabled': False})
    updated_virtual_service = pce.virtual_services.get_by_reference(mock_virtual_service.href)
    assert updated_virtual_service.enabled is False
