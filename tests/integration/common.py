import pytest

from illumio.policyobjects import (
    Label,
    LabelSet,
    Service,
    ServicePort
)
from illumio.rules import RuleSet
from illumio.workloads import Workload

from helpers import random_string


@pytest.fixture
def role_label(pce, session_identifier):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='role',
            value='{}-R-{}'.format(session_identifier, identifier),
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


@pytest.fixture
def app_label(pce, session_identifier):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='app',
            value='{}-A-{}'.format(session_identifier, identifier),
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


@pytest.fixture
def env_label(pce, session_identifier):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='env',
            value='{}-E-{}'.format(session_identifier, identifier),
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


@pytest.fixture
def loc_label(pce, session_identifier):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='loc',
            value='{}-L-{}'.format(session_identifier, identifier),
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


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


@pytest.fixture
def rule_set(pce, session_identifier, app_label, env_label, loc_label):
    identifier = random_string()
    rule_set = pce.rule_sets.create(
        RuleSet(
            name='{}-IPL-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            enabled=True,
            scopes=[LabelSet(labels=[app_label, env_label, loc_label])],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield rule_set
    pce.rule_sets.delete(rule_set.href)


@pytest.fixture
def workload(pce, session_identifier):
    identifier = random_string()
    hostname = '{}.{}'.format(session_identifier, identifier)
    workload = pce.workloads.create(
        Workload(
            name=hostname,
            hostname=hostname,
            description='Created by illumio python library integration tests',
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield workload
    pce.workloads.delete(workload.href)
