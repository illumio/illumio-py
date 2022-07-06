import pytest

from illumio.policyobjects import LabelGroup

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


def test_get_by_reference(pce, label_group):
    lg = pce.label_groups.get_by_reference(label_group.href)
    assert lg.href == label_group.href


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

    lg = pce.label_groups.get_by_reference(label_group.href)
    assert len(lg.labels) == 2
