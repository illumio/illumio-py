import pytest

from illumio.policyobjects import IPList, IPRange, FQDN
from illumio.util import DRAFT


@pytest.fixture
def ip_list(pce, object_prefix, random_string):
    ip_list = pce.ip_lists.create(
        IPList(
            name='{}-IPL-{}'.format(object_prefix, random_string),
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
            external_data_set='illumio-py-integration-tests',
            external_data_reference=random_string
        )
    )
    yield ip_list
    pce.ip_lists.delete(ip_list.href)


def test_get_by_href(pce, ip_list):
    ipl = pce.ip_lists.get_by_href(ip_list.href)
    assert ipl == ip_list


def test_get_by_partial_name(pce, object_prefix, ip_list):
    ip_lists = pce.ip_lists.get(params={'name': object_prefix}, policy_version=DRAFT)
    assert len(ip_lists) == 1


def test_update_ip_list(pce, ip_list):
    pce.ip_lists.update(
        ip_list.href,
        {
            'description': 'Integration test update. Remove FQDNs.',
            'fqdns': []
        }
    )
    ipl = pce.ip_lists.get_by_href(ip_list.href)
    assert ipl.fqdns == []


def test_provision_ip_list(pce, object_prefix, random_string):
    ip_list = pce.ip_lists.create(
        {
            'name': '{}-IPL-{}'.format(object_prefix, random_string),
            'description': 'Test IP List provisioning',
            'ip_ranges': [{'from_ip': '10.0.0.0/8'}],
            'external_data_set': 'illumio-py-integration-tests',
            'external_data_reference': random_string
        }
    )
    policy_version = pce.provision_policy_changes(
        change_description='Test IP List provisioning',
        hrefs=[ip_list.href]
    )
    assert policy_version

    pce.ip_lists.delete(ip_list.href)
    policy_version = pce.provision_policy_changes(
        change_description='Remove provisioned IP list',
        hrefs=[ip_list.href]
    )
    assert policy_version
