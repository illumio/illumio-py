import pytest

from illumio.policyobjects import ServicePort
from illumio.rules import Rule
from illumio.util import convert_protocol

from helpers import random_string


@pytest.fixture
def rule(pce, session_identifier, rule_set, role_label):
    identifier = random_string()
    any_ip_list = pce.get_default_ip_list()
    rule = pce.rules.create(
        Rule.build(
            providers=[role_label],
            consumers=[any_ip_list],
            ingress_services=[
                ServicePort(port=443, proto='tcp'),
                {'port': 8080, 'proto': convert_protocol('tcp')}
            ],
            resolve_providers_as=['workloads'],
            resolve_consumers_as=['workloads'],
            external_data_set=session_identifier,
            external_data_reference=identifier
        ),
        parent=rule_set.href
    )
    yield rule
    pce.rules.delete(rule)


def test_get_by_href(pce, rule):
    r = pce.rules.get_by_reference(rule)
    assert r.href == rule.href


def test_get_from_rule_set(pce, rule_set, rule):
    rules = pce.rules.get(parent=rule_set.href)
    assert len(rules) == 1


def test_update_rule(pce, rule):
    services = rule.ingress_services
    services.append({'port': 80, 'proto': convert_protocol('tcp')})
    pce.rules.update(rule, {'ingress_services': services})
    updated_rule = pce.rules.get_by_reference(rule)
    assert len(updated_rule.ingress_services) == 3
