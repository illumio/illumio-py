import json
import os
import re
from typing import List

import pytest
from requests_mock import ANY

from illumio.util import IllumioEncoder
from illumio.rules import Rule

MOCK_RULE = os.path.join(pytest.DATA_DIR, 'rule.json')


@pytest.fixture(scope='module')
def mock_rule() -> List[Rule]:
    with open(MOCK_RULE, 'r') as f:
        yield Rule.from_json(json.loads(f.read()))


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_rule):
    matcher = re.compile('/sec_rules')
    requests_mock.register_uri(ANY, matcher, json=json.dumps(mock_rule, cls=IllumioEncoder))


def test_label_resolution_block(mock_rule):
    json_rule = mock_rule.to_json()
    assert json_rule['resolve_labels_as']['providers'] == ['workloads']


def test_builder(mock_rule):
    rule = Rule.build(
        providers=["/orgs/1/labels/1"],
        consumers=["ams"],
        ingress_services=[{"port": 1234, "proto": 6}],
        resolve_providers_as=["workloads"],
        resolve_consumers_as=["workloads"]
    )
    expected_result = json.loads('''
        {
            "ingress_services": [
                {"port": 1234, "proto": 6}
            ],
            "providers": [
                {"label": {"href": "/orgs/1/labels/1"}}
            ],
            "consumers": [
                {"actors": "ams"}
            ],
            "resolve_labels_as": {
                "providers": ["workloads"],
                "consumers": ["workloads"]
            }
        }
    ''')
    assert rule.to_json() == expected_result
