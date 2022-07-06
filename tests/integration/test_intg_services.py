from illumio.policyobjects import ServicePort
from illumio.util import convert_protocol, DRAFT


def test_get_by_reference(pce, web_service):
    service = pce.services.get_by_reference(web_service.href)
    assert service.href == web_service.href


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
    service = pce.services.get_by_reference(well_known_service.href)
    assert service.service_ports == updated_service_ports
