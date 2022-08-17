import json
import os
import re
from typing import List

import pytest

from illumio.workloads import VEN

VENS = os.path.join(pytest.DATA_DIR, 'vens.json')


@pytest.fixture(scope='module')
def vens() -> List[dict]:
    with open(VENS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def vens_mock(pce_object_mock, vens):
    pce_object_mock.add_mock_objects(vens)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback):
    pattern = re.compile('/vens')
    requests_mock.register_uri('GET', pattern, json=get_callback)


@pytest.fixture()
def mock_ven(pce) -> VEN:
    yield pce.vens.get_by_reference("/orgs/1/vens/ec38510d-e4fd-41a1-a6ba-8b0bb4ce9ae9")


def test_get_by_hostname(pce, mock_ven):
    ven = pce.vens.get(params={'hostname': 'WIN-CK9JH7R07NB'})[0]
    assert ven == mock_ven
