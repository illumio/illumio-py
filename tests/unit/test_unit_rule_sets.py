import json
import os
import re
from typing import List

import pytest

from illumio.policyobjects import LabelSet
from illumio.rules import RuleSet
from illumio.util import Reference, DRAFT, ACTIVE

RULESETS = os.path.join(pytest.DATA_DIR, 'rule_sets.json')


@pytest.fixture(scope='module')
def rule_sets() -> List[dict]:
    with open(RULESETS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def new_rule_set() -> RuleSet:
    return RuleSet(
        name="RS-TEST"
    )


@pytest.fixture(autouse=True)
def rule_sets_mock(pce_object_mock, rule_sets):
    pce_object_mock.add_mock_objects(rule_sets)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/sec_policy/(draft|active)/rule_sets')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


@pytest.fixture()
def mock_rule_set(pce) -> RuleSet:
    yield pce.rule_sets.get_by_reference("/orgs/1/sec_policy/active/rule_sets/1")


def test_encoded_scopes(pce):
    rule_set = pce.rule_sets.get_by_reference("/orgs/1/sec_policy/draft/rule_sets/2")
    json_rule_set = rule_set.to_json()
    assert json_rule_set['scopes'] == [[]]


def test_compare_unordered_scopes(mock_rule_set):
    scopes = [
        LabelSet(
            labels=[
                Reference(href="/orgs/1/labels/24"),
                Reference(href="/orgs/1/labels/22"),
                Reference(href="/orgs/1/labels/23")
            ]
        )
    ]
    assert mock_rule_set.scopes == scopes


def test_get_by_name(pce):
    rule_sets = pce.rule_sets.get(params={'name': 'RS-'}, policy_version=DRAFT)
    assert len(rule_sets) == 2


def test_get_active_rule_sets(pce, mock_rule_set):
    rule_set = pce.rule_sets.get(params={'name': 'RS-RINGFENCE', 'max_results': 1}, policy_version=ACTIVE)[0]
    assert rule_set == mock_rule_set


def test_create_rule_set(pce, new_rule_set):
    created_rule_set = pce.rule_sets.create(new_rule_set)
    assert created_rule_set.href != ''
    rule_set = pce.rule_sets.get_by_reference(created_rule_set.href)
    assert created_rule_set == rule_set


def test_update_rule_set(pce, mock_rule_set):
    pce.rule_sets.update(mock_rule_set.href, {'enabled': False})
    updated_rule_set = pce.rule_sets.get_by_reference(mock_rule_set.href)
    assert updated_rule_set.enabled is False
