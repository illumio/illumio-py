import json
import os
import re
from typing import List

import pytest

from illumio.policyobjects import Service, ServicePort
from illumio.util import IllumioEncoder, convert_protocol, DRAFT, ACTIVE

SERVICES = os.path.join(pytest.DATA_DIR, 'services.json')
DEFAULT_SERVICE_NAME = 'All Services'


@pytest.fixture(scope='module')
def services() -> List[dict]:
    with open(SERVICES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def web_service() -> Service:
    return Service(
        name='S-Web',
        service_ports=[
            ServicePort(port=443, proto='tcp'),
            ServicePort(port=80, proto='tcp'),
        ]
    )


@pytest.fixture(autouse=True)
def services_mock(pce_object_mock, services):
    pce_object_mock.add_mock_objects(services)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/sec_policy/(draft|active)/services')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


def test_compare_service_ports(pce, web_service):
    http_service = pce.services.get(params={'name': 'S-HTTP', 'max_results': 1})[0]
    assert len(web_service.service_ports) == len(http_service.service_ports)
    assert set([(sp.port, sp.proto) for sp in web_service.service_ports]) == set([(sp.port, sp.proto) for sp in http_service.service_ports])


def test_proto_encoding():
    https_service_port = ServicePort(port=443, proto='tcp')
    assert https_service_port.proto == convert_protocol('tcp')
    encoded_https_service_port = json.loads(json.dumps(https_service_port, cls=IllumioEncoder))
    assert encoded_https_service_port == {'port': 443, 'proto': 6}


def test_get_default_service(pce):
    default_service = pce.services.get(params={'name': DEFAULT_SERVICE_NAME, 'max_results': 1}, policy_version=ACTIVE)[0]
    assert default_service.name == DEFAULT_SERVICE_NAME


def test_get_by_reference(pce):
    any_service = pce.services.get_by_reference('/orgs/1/sec_policy/active/services/1')
    assert any_service.name == DEFAULT_SERVICE_NAME


def test_get_by_name(pce):
    services = pce.services.get(params={'name': 'S-'}, policy_version=DRAFT)
    assert len(services) == 2


def test_get_active_service(pce):
    services = pce.services.get(params={'name': 'S-'}, policy_version=ACTIVE)
    assert len(services) == 0


def test_create_service(pce, web_service):
    service = pce.services.create(web_service)
    assert service.href != ''
    fetched_service = pce.services.get_by_reference(service.href)
    assert fetched_service == service


def test_update_service(pce):
    service = pce.services.get(params={'name': 'S-HTTP', 'max_results': 1})[0]
    pce.services.update(service.href, {'service_ports': [ServicePort(port=8080, proto='tcp')]})
    updated_service = pce.services.get_by_reference(service.href)
    print(updated_service)
    assert len(updated_service.service_ports) > 0
    assert updated_service.service_ports[0].port == 8080
