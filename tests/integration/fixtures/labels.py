import pytest

from illumio.policyobjects import Label

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

__all__ = [
    'role_label',
    'app_label',
    'env_label',
    'loc_label'
]
