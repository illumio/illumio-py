import os

import pytest

from illumio import PolicyComputeEngine
from mocks import (
    PolicyObjectMock as _PolicyObjectMock,
    PceObjectMock as _PceObjectMock
)

TEST_DIR = os.path.abspath(os.path.dirname(__file__))


def pytest_configure():
    pytest.DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.fixture(scope='session')
def pce():
    return PolicyComputeEngine('test.pce.com', port=443)


@pytest.fixture(scope='session')
def PceObjectMock():
    return _PceObjectMock


@pytest.fixture(scope='session')
def PolicyObjectMock():
    return _PolicyObjectMock
