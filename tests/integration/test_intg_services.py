from illumio.policyobjects import ServicePort
from illumio.util import (
    convert_protocol,
    convert_draft_href_to_active,
    DRAFT,
    ACTIVE
)

from helpers import random_string


def test_get_by_href(pce, web_service):
    service = pce.services.get_by_href(web_service.href)
    assert service == web_service


def test_get_by_partial_name(pce, session_identifier, web_service, well_known_service):
    services = pce.services.get(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(services) == 2


def test_get_by_port(pce, session_identifier, web_service, well_known_service, rdp_service):
    services = pce.services.get(params={'port': 443, 'name': session_identifier}, policy_version=DRAFT)
    assert len(services) == 2


def test_get_by_proto(pce, session_identifier, web_service, well_known_service, rdp_service):
    services = pce.services.get(params={'proto': convert_protocol('udp'), 'name': session_identifier}, policy_version=DRAFT)
    assert len(services) == 1


def test_get_async(pce, session_identifier, web_service, well_known_service, rdp_service):
    services = pce.services.get_async(params={'name': session_identifier})
    assert len(services) == 3


def test_update_service(pce, well_known_service):
    updated_service_ports = well_known_service.service_ports
    updated_service_ports.append(ServicePort.from_json({'port': 1, 'to_port': 1023, 'proto': 'udp'}))
    pce.services.update(well_known_service.href, {'service_ports': updated_service_ports})
    service = pce.services.get_by_href(well_known_service.href)
    assert service.service_ports == updated_service_ports


def test_provision_service(pce, session_identifier, request):
    identifier = random_string()
    service = pce.services.create(
        {
            'name': '{}-S-MYSQL-{}'.format(session_identifier, identifier),
            'description': 'Test service provisioning',
            'service_ports': [{'port': 3306, 'proto': convert_protocol('tcp')}],
            'external_data_set': session_identifier,
            'external_data_reference': identifier
        }
    )
    pce.provision_policy_changes(
        change_description='Test service provisioning',
        hrefs=[service.href]
    )

    def _teardown():
        pce.services.delete(service.href)
        pce.provision_policy_changes(
            change_description='Remove provisioned service',
            hrefs=[service.href]
        )

    request.addfinalizer(_teardown)

    services = pce.services.get(params={'name': session_identifier}, policy_version=ACTIVE)
    assert len(services) == 1 and services[0].href == convert_draft_href_to_active(service.href)
