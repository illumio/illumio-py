import pytest

from illumio.workloads import Workload

from helpers import random_string


@pytest.fixture
def workload(pce, session_identifier):
    identifier = random_string()
    hostname = '{}.{}'.format(session_identifier, identifier)
    workload = pce.workloads.create(
        Workload(
            name=hostname,
            hostname=hostname,
            description='Created by illumio python library integration tests',
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield workload
    pce.workloads.delete(workload.href)

__all__ = ['workload']
