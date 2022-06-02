import pytest

from illumio.policyobjects import LabelGroup
from illumio.util import convert_draft_href_to_active, ACTIVE

from helpers import random_string


@pytest.fixture
def label_group(pce, session_identifier, role_label):
    identifier = random_string()
    label_group = pce.label_groups.create(
        LabelGroup(
            key='role',
            name='{}-LG-R-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            labels=[role_label],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield label_group
    pce.label_groups.delete(label_group.href)


def test_get_by_href(pce, label_group):
    lg = pce.label_groups.get_by_href(label_group.href)
    assert lg == label_group


def test_get_by_key(pce, session_identifier, label_group):
    label_groups = pce.label_groups.get(params={'key': 'role', 'name': session_identifier})
    assert len(label_groups) == 1


def test_get_async(pce, session_identifier, label_group):
    label_groups = pce.label_groups.get_async(params={'name': session_identifier})
    assert len(label_groups) == 1


def test_add_label_to_group(pce, session_identifier, label_group, request):
    identifier = random_string()
    role_label = pce.labels.create({
        'key': 'role',
        'value': '{}-R-{}'.format(session_identifier, identifier),
        'external_data_set': session_identifier,
        'external_data_reference': identifier
    })

    def _teardown():
        pce.label_groups.update(label_group.href, {'labels': []})
        pce.labels.delete(role_label.href)

    request.addfinalizer(_teardown)

    label_group.labels.append(role_label)
    pce.label_groups.update(label_group.href, {
        'labels': label_group.labels
    })

    lg = pce.label_groups.get_by_href(label_group.href)
    assert len(lg.labels) == 2


def test_provision_label_group(pce, session_identifier, env_label, request):
    identifier = random_string()
    label_group = pce.label_groups.create(
        {
            'key': 'env',
            'name': '{}-LG-E-{}'.format(session_identifier, identifier),
            'description': 'Created by illumio python library integration tests',
            'labels': [env_label],
            'external_data_set': session_identifier,
            'external_data_reference': identifier
        }
    )
    pce.provision_policy_changes(
        change_description='Test label group provisioning',
        hrefs=[label_group.href]
    )

    def _teardown():
        pce.label_groups.delete(label_group.href)
        pce.provision_policy_changes(
            change_description='Remove provisioned label group',
            hrefs=[label_group.href]
        )

    request.addfinalizer(_teardown)

    label_groups = pce.label_groups.get(params={'name': session_identifier}, policy_version=ACTIVE)
    assert len(label_groups) == 1 and label_groups[0].href == convert_draft_href_to_active(label_group.href)
