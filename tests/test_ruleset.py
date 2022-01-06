import json
import os
import re

import pytest
from requests_mock import ANY

from illumio.util import IllumioEncoder
from illumio.rules import Ruleset

MOCK_RULESET = os.path.join(pytest.DATA_DIR, 'ruleset.json')


@pytest.fixture(scope='module')
def mock_ruleset() -> Ruleset:
    with open(MOCK_RULESET, 'r') as f:
        yield Ruleset.from_json(f.read())


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_ruleset):
    matcher = re.compile('/sec_policy/draft/rule_sets')
    requests_mock.register_uri(ANY, matcher, json=json.dumps(mock_ruleset, cls=IllumioEncoder))


def test_encoded_scopes(mock_ruleset):
    json_ruleset = mock_ruleset.to_json()
    assert json_ruleset['scopes'] == [[]]
