import pytest

from illumio.policyobjects import IPList, IPRange, FQDN
from illumio.util import DRAFT

from helpers import random_string


@pytest.fixture
def ip_list(pce, session_identifier):
    identifier = random_string()
    ip_list = pce.ip_lists.create(
        IPList(
            name='{}-IPL-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            ip_ranges=[
                IPRange(
                    from_ip='192.168.0.0/16',
                    description='Local network addresses'
                ),
                IPRange(
                    from_ip='10.0.0.1',
                    to_ip='10.0.1.255',
                    description='Private addresses'
                ),
                {'from_ip': '127.0.0.1', 'description': 'Loopback address'},
                {'from_ip': '192.168.0.1', 'exclusion': True, 'description': 'Exclude router address'}
            ],
            fqdns=[
                FQDN(fqdn='*.internal.labs.io', description='Internal lab domains'),
                {'fqdn': 'localhost', 'description': 'Local hostname'}
            ],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield ip_list
    pce.ip_lists.delete(ip_list.href)


def test_get_by_reference(pce, ip_list):
    ipl = pce.ip_lists.get_by_reference(ip_list.href)
    assert ipl.href == ip_list.href


def test_get_by_partial_name(pce, session_identifier, ip_list):
    ip_lists = pce.ip_lists.get(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(ip_lists) == 1


def test_get_by_ip(pce, session_identifier, ip_list):
    ip_lists = pce.ip_lists.get(params={'name': session_identifier, 'ip_list': '192.168.123.255'}, policy_version=DRAFT)
    assert len(ip_lists) == 1


def test_get_by_fqdn(pce, session_identifier, ip_list):
    ip_lists = pce.ip_lists.get(params={'name': session_identifier, 'fqdn': 'internal.labs.io'}, policy_version=DRAFT)
    assert len(ip_lists) == 1


def test_get_async(pce, session_identifier, ip_list):
    ip_lists = pce.ip_lists.get_async(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(ip_lists) == 1


def test_update_ip_list(pce, ip_list):
    pce.ip_lists.update(
        ip_list.href,
        {
            'description': 'Integration test update. Remove FQDNs.',
            'fqdns': []
        }
    )
    ipl = pce.ip_lists.get_by_reference(ip_list.href)
    assert ipl.fqdns == []
