import json
import os
import re
from typing import List

import pytest

LABEL_GROUPS = os.path.join(pytest.DATA_DIR, 'label_groups.json')


@pytest.fixture(scope='module')
def label_groups() -> List[dict]:
    with open(LABEL_GROUPS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def label_groups_mock(pce_object_mock, label_groups):
    pce_object_mock.add_mock_objects(label_groups)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/sec_policy/(draft|active)/label_groups')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


def test_nested_label_groups(pce):
    label_group = pce.label_groups.get_by_name(name="LG-L-Datacenters")
    assert len(label_group.sub_groups) > 0
