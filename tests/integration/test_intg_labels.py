from helpers import random_string


def test_get_by_href(pce, role_label):
    label = pce.labels.get_by_href(role_label.href)
    assert label == role_label


def test_get_by_partial_name(pce, object_prefix, role_label, app_label, env_label, loc_label):
    labels = pce.labels.get(params={'value': object_prefix})
    assert len(labels) == 4


def test_get_by_key(pce, object_prefix, role_label, app_label):
    labels = pce.labels.get(params={'key': 'role', 'value': object_prefix})
    assert len(labels) == 1


def test_get_async(pce, object_prefix, role_label):
    labels = pce.labels.get_async(params={'value': object_prefix})
    assert len(labels) == 1


def test_create_label(pce, object_prefix):
    identifier = random_string()
    label = pce.labels.create({
        'key': 'role',
        'value': '{}-R-{}'.format(object_prefix, identifier),
        'external_data_set': 'illumio-py-integration-tests',
        'external_data_reference': identifier
    })
    assert label.href
    pce.labels.delete(label.href)


def test_update_label(pce, object_prefix, env_label):
    updated_value = '{}-A-UPDATED'.format(object_prefix)
    pce.labels.update(
        env_label.href,
        {
            'value': updated_value
        }
    )
    label = pce.labels.get_by_href(env_label.href)
    assert label.value == updated_value
