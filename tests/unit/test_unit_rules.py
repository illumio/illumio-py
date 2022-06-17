import json
import os
import re
from typing import List

import pytest
from requests_mock import ANY

from illumio.rules import Rule

MOCK_RULES = os.path.join(pytest.DATA_DIR, 'rules.json')
MOCK_RULE_SET_HREF = '/orgs/1/sec_policy/draft/rule_sets/1'


@pytest.fixture(scope='module')
def rules() -> List[Rule]:
    with open(MOCK_RULES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def rules_mock(pce_object_mock, rules):
    pce_object_mock.add_mock_objects(rules)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/sec_rules')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


@pytest.fixture()
def mock_rule(pce) -> Rule:
    yield pce.rules.get_by_reference('{}/sec_rules/1'.format(MOCK_RULE_SET_HREF))


def test_label_resolution_block(mock_rule):
    json_rule = mock_rule.to_json()
    assert json_rule['resolve_labels_as']['providers'] == ['workloads']


def test_builder():
    rule = Rule.build(
        providers=['/orgs/1/labels/1'],
        consumers=['ams'],
        ingress_services=[{'port': 1234, 'proto': 6}],
        resolve_providers_as=['workloads'],
        resolve_consumers_as=['workloads']
    )
    expected_result = json.loads('''
        {
            "enabled": true,
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


def test_get_rules(pce):
    rules = pce.rules.get(parent=MOCK_RULE_SET_HREF)
    assert len(rules) > 0
