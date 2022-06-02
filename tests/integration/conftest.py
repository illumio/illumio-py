import os

import pytest

from illumio import PolicyComputeEngine, IllumioException
from illumio.util import PCE_APIS

from helpers import random_string

# environment variables for integration tests
pce_host = os.getenv('ILLUMIO_PCE_HOST')
pce_port = os.getenv('ILLUMIO_PCE_PORT', 443)
org_id = os.getenv('ILLUMIO_PCE_ORG_ID', 1)
api_key = os.getenv('ILLUMIO_API_KEY_USERNAME')
api_secret = os.getenv('ILLUMIO_API_KEY_SECRET')


@pytest.fixture(scope='session')
def pce():
    if not pce_host or not api_key or not api_secret:
        raise IllumioException('''Missing required environment variable for integration tests.
Make sure ILLUMIO_PCE_HOST, ILLUMIO_API_KEY_USERNAME, and ILLUMIO_API_KEY_SECRET are set.''')
    pce = PolicyComputeEngine(pce_host, port=pce_port, org_id=org_id)
    pce.set_credentials(api_key, api_secret)
    return pce


@pytest.fixture(scope='session')
def session_identifier():
    return 'illumio-py-integration-{}'.format(random_string())


@pytest.fixture(scope='session', autouse=True)
def cleanup(pce, session_identifier, request):
    def _teardown():
        for name in PCE_APIS.keys():
            api = getattr(pce, name)
            try:
                leftover_integration_objects = api.get(
                    params={'external_data_set': session_identifier}
                )
                for o in leftover_integration_objects:
                    api.delete(o.href)
            except IllumioException:
                pass
    request.addfinalizer(_teardown)


# prepare common fixtures
from common import *
