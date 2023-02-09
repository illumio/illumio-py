import pytest

from illumio import PolicyComputeEngine, IllumioApiException

from helpers import pce_from_env

INVALID_PCE_HOSTNAME = 'invalid.url.comxyz'


# use a local test fixture so we don't manipulate the session-scoped PCE
@pytest.fixture
def test_pce() -> PolicyComputeEngine:
    pce = pce_from_env(retry_count=0)
    yield pce


def test_invalid_hostname(test_pce: PolicyComputeEngine):
    test_pce._hostname = INVALID_PCE_HOSTNAME
    with pytest.raises(IllumioApiException):
        test_pce.get('/health')


def test_invalid_endpoint(test_pce: PolicyComputeEngine):
    with pytest.raises(IllumioApiException):
        test_pce.get('/invalid_endpoint')


def test_invalid_org_id(test_pce: PolicyComputeEngine):
    test_pce.org_id = 0
    assert not test_pce.check_connection()


def test_must_connect(test_pce: PolicyComputeEngine):
    test_pce._hostname = INVALID_PCE_HOSTNAME
    with pytest.raises(IllumioApiException):
        test_pce.must_connect()
