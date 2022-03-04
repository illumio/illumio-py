import json
import os
import re

import pytest
from requests_mock import ANY

from illumio import PolicyComputeEngine
from illumio.rules import Ruleset

MOCK_RULESET = os.path.join(pytest.DATA_DIR, 'ruleset.json')
DRAFT_RULESETS = os.path.join(pytest.DATA_DIR, 'draft_rulesets.json')
ACTIVE_RULESETS = os.path.join(pytest.DATA_DIR, 'active_rulesets.json')


@pytest.fixture(scope='module')
def draft_rulesets() -> list:
    with open(DRAFT_RULESETS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def active_rulesets() -> list:
    with open(ACTIVE_RULESETS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def new_ruleset() -> Ruleset:
    return Ruleset(
        name="RS-TEST"
    )


@pytest.fixture(scope='module')
def get_callback(PolicyUtil, draft_rulesets, active_rulesets):
    def _callback_fn(request, context):
        policy_util = PolicyUtil(draft_rulesets, active_rulesets)
        return policy_util.get_mock_objects(request.path_url)
    return _callback_fn


@pytest.fixture(scope='module')
def post_callback(new_ruleset):
    def _callback_fn(request, context):
        return new_ruleset.to_json()
    return _callback_fn


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback):
    pattern = re.compile('/sec_policy/(draft|active)/rule_sets')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)


@pytest.fixture()
def mock_ruleset(pce: PolicyComputeEngine) -> Ruleset:
    yield pce.get_ruleset("/orgs/1/sec_policy/draft/rule_sets/1")


def test_encoded_scopes(mock_ruleset):
    json_ruleset = mock_ruleset.to_json()
    assert json_ruleset['scopes'] == [[]]


def test_get_by_name_deprecation(pce: PolicyComputeEngine):
    with pytest.deprecated_call():
        pce.get_rulesets_by_name(name="TEST")
