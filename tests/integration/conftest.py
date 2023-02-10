import pytest

from helpers import random_string, pce_from_env
from sweepers import Sweeper


@pytest.fixture(scope='session')
def pce():
    _pce = pce_from_env()
    _pce.must_connect()
    yield _pce


@pytest.fixture(scope='session')
def session_identifier():
    return 'illumio-py-integration-{}'.format(random_string())


@pytest.fixture(scope='session', autouse=True)
def cleanup(pce, session_identifier, request):
    def _teardown():
        sweeper = Sweeper(pce, session_identifier)
        sweeper.sweep()
    request.addfinalizer(_teardown)


# prepare common fixtures
from fixtures import *
