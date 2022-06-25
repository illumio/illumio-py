import pytest

from illumio.policyobjects import Service, ServicePort

from helpers import random_string


@pytest.fixture
def web_service(pce, session_identifier):
    identifier = random_string()
    service = pce.services.create(
        Service(
            name='{}-S-WEB-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            service_ports=[
                ServicePort(port=80, proto='tcp'),
                ServicePort(port=443, proto='tcp')
            ],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield service
    pce.services.delete(service.href)


@pytest.fixture
def well_known_service(pce, session_identifier):
    identifier = random_string()
    service = pce.services.create(
        Service(
            name='{}-S-WELL-KNOWN-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            service_ports=[
                ServicePort(port=1, to_port=1023, proto='tcp')
            ],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield service
    pce.services.delete(service.href)


@pytest.fixture
def rdp_service(pce, session_identifier):
    identifier = random_string()
    service = pce.services.create(
        Service(
            name='{}-S-RDP-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            service_ports=[
                ServicePort(port=3389, proto='tcp'),
                ServicePort(port=3389, proto='udp')
            ],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield service
    pce.services.delete(service.href)

__all__ = [
    'web_service',
    'well_known_service',
    'rdp_service'
]
