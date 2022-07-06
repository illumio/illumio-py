from helpers import random_string


def test_get_by_reference(pce, role_label):
    label = pce.labels.get_by_reference(role_label.href)
    assert label.href == role_label.href


def test_get_by_partial_name(pce, session_identifier, role_label, app_label, env_label, loc_label):
    labels = pce.labels.get(params={'value': session_identifier})
    assert len(labels) == 4


def test_get_by_key(pce, session_identifier, role_label, app_label):
    labels = pce.labels.get(params={'key': 'role', 'value': session_identifier})
    assert len(labels) == 1


def test_get_async(pce, session_identifier, role_label):
    labels = pce.labels.get_async(params={'value': session_identifier})
    assert len(labels) == 1


def test_create_label(pce, session_identifier):
    identifier = random_string()
    label = pce.labels.create({
        'key': 'role',
        'value': '{}-R-{}'.format(session_identifier, identifier),
        'external_data_set': session_identifier,
        'external_data_reference': identifier
    })
    assert label.href
    pce.labels.delete(label.href)


def test_update_label(pce, session_identifier, env_label):
    updated_value = '{}-E-UPDATED'.format(session_identifier)
    pce.labels.update(
        env_label.href,
        {
            'value': updated_value
        }
    )
    label = pce.labels.get_by_reference(env_label.href)
    assert label.value == updated_value
