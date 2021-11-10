import os
import re

import pytest
from requests_mock import ANY

from illumio import (
    TrafficQuery,
    TrafficQueryFilterBlock
)

MOCK_TRAFFIC_QUERY = os.path.join(pytest.DATA_DIR, 'traffic_query.json')


@pytest.fixture(scope='module')
def mock_traffic_query() -> TrafficQuery:
    with open(MOCK_TRAFFIC_QUERY, 'r') as f:
        yield TrafficQuery.from_json(f.read())


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_traffic_query):
    matcher = re.compile('/traffic_flows/traffic_analysis_queries')
    requests_mock.register_uri(ANY, matcher, json=mock_traffic_query.to_json())


def test_decoded_structure(mock_traffic_query):
    assert type(mock_traffic_query.sources) is TrafficQueryFilterBlock
