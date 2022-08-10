import pytest

from illumio.policyobjects import ServicePort
from illumio.rules import EnforcementBoundary
from illumio.util import convert_protocol, DRAFT, AMS

from helpers import random_string


@pytest.fixture
def enforcement_boundary(pce, session_identifier, rdp_service):
    identifier = random_string()
    any_enforcement_boundary = pce.get_default_ip_list()
    enforcement_boundary = pce.enforcement_boundaries.create(
        EnforcementBoundary.build(
            name='{}-EB-{}'.format(session_identifier, identifier),
            ingress_services=[rdp_service, {'port': 20009, 'proto': convert_protocol('tcp')}],
            providers=[AMS],
            consumers=[any_enforcement_boundary]
        )
    )
    yield enforcement_boundary
    pce.enforcement_boundaries.delete(enforcement_boundary.href)


def test_get_by_reference(pce, enforcement_boundary):
    eb = pce.enforcement_boundaries.get_by_reference(enforcement_boundary.href)
    assert eb.href == enforcement_boundary.href


def test_get_by_partial_name(pce, session_identifier, enforcement_boundary):
    enforcement_boundaries = pce.enforcement_boundaries.get(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(enforcement_boundaries) == 1


def test_get_async(pce, session_identifier, enforcement_boundary):
    enforcement_boundaries = pce.enforcement_boundaries.get_async(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(enforcement_boundaries) == 1


def test_update_enforcement_boundary(pce, enforcement_boundary):
    services = enforcement_boundary.ingress_services
    services.append(ServicePort(port=20009, proto='udp'))
    pce.enforcement_boundaries.update(
        enforcement_boundary.href, {'ingress_services': services}
    )
    eb = pce.enforcement_boundaries.get_by_reference(enforcement_boundary.href)
    assert len(eb.ingress_services) == 3
