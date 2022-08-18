import pytest

from illumio.policyobjects import (
    VirtualService,
    ServiceBinding,
    ServicePort,
    ServiceAddress
)
from illumio.util import (
    ApplyTo,
    convert_draft_href_to_active,
    convert_active_href_to_draft,
    convert_protocol,
    DRAFT
)

from helpers import random_string


@pytest.fixture
def virtual_service(pce, session_identifier):
    identifier = random_string()
    virtual_service = pce.virtual_services.create(
        {
            'name': '{}-VS-{}'.format(session_identifier, identifier),
            'description': 'Created by illumio python library integration tests',
            'service_ports': [{'port': 137, 'proto': convert_protocol('udp')}]
        }
    )
    yield virtual_service
    pce.virtual_services.delete(virtual_service.href)


@pytest.fixture
def active_virtual_service(pce, session_identifier, env_label, loc_label):
    identifier = random_string()
    virtual_service = pce.virtual_services.create(
        VirtualService(
            name='{}-VS-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            apply_to=ApplyTo.HOST_ONLY,
            service_addresses=[
                ServiceAddress(fqdn='localhost.localdomain')
            ],
            service_ports=[
                ServicePort(port=80, proto='tcp')
            ],
            labels=[env_label, loc_label],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )

    pce.provision_policy_changes(
        change_description='Provision virtual service',
        hrefs=[virtual_service.href]
    )

    # service bindings must be created using an active virtual service
    virtual_service.href = convert_draft_href_to_active(virtual_service.href)

    yield virtual_service

    # to delete an active object, a DELETE call needs to be made against the
    # draft HREF and then provisioned
    virtual_service.href = convert_active_href_to_draft(virtual_service.href)

    pce.virtual_services.delete(virtual_service.href)
    pce.provision_policy_changes(
        change_description='Remove provisioned virtual service',
        hrefs=[virtual_service.href]
    )


@pytest.fixture
def service_binding(pce, active_virtual_service, workload):
    results = pce.service_bindings.create(
        [ServiceBinding(virtual_service=active_virtual_service, workload=workload)]
    )
    service_binding = results['service_bindings'][0]
    yield service_binding
    pce.service_bindings.delete(service_binding.href)


def test_get_by_reference(pce, virtual_service):
    vs = pce.virtual_services.get_by_reference(virtual_service.href)
    assert vs.href == virtual_service.href


def test_get_by_partial_name(pce, session_identifier, virtual_service):
    virtual_services = pce.virtual_services.get(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(virtual_services) == 1


def test_get_by_service_port(pce, virtual_service):
    virtual_services = pce.virtual_services.get(params={'service_ports.port': 137}, policy_version=DRAFT)
    assert len(virtual_services) == 1


def test_get_async(pce, session_identifier, virtual_service):
    virtual_services = pce.virtual_services.get_async(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(virtual_services) == 1


def test_update_virtual_service(pce, session_identifier, virtual_service):
    fqdn = '{}.localhost.localdomain'.format(session_identifier)
    pce.virtual_services.update(
        virtual_service.href,
        {
            'description': 'Integration test update. Add service address.',
            'service_addresses': [{'fqdn': fqdn}]
        }
    )
    virtual_services = pce.virtual_services.get(params={'service_address.fqdn': fqdn}, policy_version=DRAFT)
    vs = virtual_services[0]
    assert vs.href == virtual_service.href and vs.service_addresses[0].fqdn == fqdn


def test_get_service_binding_by_href(pce, service_binding):
    binding = pce.service_bindings.get_by_reference(service_binding.href)
    assert binding.href == service_binding.href


def test_get_service_bindings_by_virtual_service(pce, active_virtual_service, service_binding):
    bindings = pce.service_bindings.get(params={'virtual_service': active_virtual_service.href})
    assert len(bindings) == 1
