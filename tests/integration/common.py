import pytest

from illumio.policyobjects import Label

from helpers import random_string


@pytest.fixture
def role_label(pce, object_prefix):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='role',
            value='{}-R-{}'.format(object_prefix, identifier),
            external_data_set='illumio-py-integration-tests',
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


@pytest.fixture
def app_label(pce, object_prefix):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='app',
            value='{}-A-{}'.format(object_prefix, identifier),
            external_data_set='illumio-py-integration-tests',
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


@pytest.fixture
def env_label(pce, object_prefix):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='env',
            value='{}-E-{}'.format(object_prefix, identifier),
            external_data_set='illumio-py-integration-tests',
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)


@pytest.fixture
def loc_label(pce, object_prefix):
    identifier = random_string()
    label = pce.labels.create(
        Label(
            key='loc',
            value='{}-L-{}'.format(object_prefix, identifier),
            external_data_set='illumio-py-integration-tests',
            external_data_reference=identifier
        )
    )
    yield label
    pce.labels.delete(label.href)
