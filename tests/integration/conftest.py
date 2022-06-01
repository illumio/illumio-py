import os

import pytest

from illumio import PolicyComputeEngine

# environment variables for integration tests
pce_host = os.getenv('ILLUMIO_PCE_HOST', 'test.pce.com')
pce_port = os.getenv('ILLUMIO_PCE_PORT', 443)
org_id = os.getenv('ILLUMIO_PCE_ORG_ID', 1)
api_key = os.getenv('ILLUMIO_API_KEY_USERNAME', '')
api_secret = os.getenv('ILLUMIO_API_KEY_SECRET', '')


@pytest.fixture(scope='session')
def pce():
    pce = PolicyComputeEngine(pce_host, port=pce_port, org_id=org_id)
    pce.set_credentials(api_key, api_secret)
    return pce


@pytest.fixture(scope='session')
def test_prefix():
    return 'TEST-INTEGRATION'
