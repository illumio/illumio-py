import os
import pytest

from illumio import PolicyComputeEngine

TEST_DIR = os.path.abspath(os.path.dirname(__file__))


def pytest_configure():
    pytest.DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.fixture(scope='session')
def pce():
    return PolicyComputeEngine('crest-mnc.ilabs.io', port=8443)
