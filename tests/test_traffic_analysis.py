import json
import os
import re
from datetime import datetime, timezone
from typing import List

import pytest
from requests_mock import ANY

from illumio import IllumioException
from illumio.util import IllumioEncoder
from illumio.explorer import TrafficQuery, TrafficQueryFilterBlock, TrafficFlow

MOCK_TRAFFIC_QUERY = os.path.join(pytest.DATA_DIR, 'traffic_query.json')
MOCK_TRAFFIC_RESPONSE = os.path.join(pytest.DATA_DIR, 'traffic_query_response.json')


@pytest.fixture(scope='module')
def mock_traffic_query() -> TrafficQuery:
    with open(MOCK_TRAFFIC_QUERY, 'r') as f:
        yield TrafficQuery.from_json(f.read())


@pytest.fixture(scope='module')
def mock_traffic_response() -> List[TrafficFlow]:
    with open(MOCK_TRAFFIC_RESPONSE, 'r') as f:
        yield [TrafficFlow.from_json(o) for o in json.loads(f.read())]


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, mock_traffic_response):
    matcher = re.compile('/traffic_flows/traffic_analysis_queries')
    traffic_response_json = [json.dumps(flow, cls=IllumioEncoder) for flow in mock_traffic_response]
    requests_mock.register_uri(ANY, matcher, json=traffic_response_json)


def test_query_structure(mock_traffic_query):
    assert type(mock_traffic_query.sources) is TrafficQueryFilterBlock


def test_traffic_query(pce, mock_traffic_query):
    traffic_flows = pce.get_traffic_flows(mock_traffic_query)
    assert len(traffic_flows) > 1


def test_invalid_policy_decision():
    with pytest.raises(IllumioException):
        TrafficQuery(start_date='2021-11-05', end_date='2021-11-12', policy_decisions=["invalid_policy_decision"])


def test_response_structure(mock_traffic_response):
    assert len(mock_traffic_response) > 1
    assert mock_traffic_response[0].src is not None


def test_traffic_query_builder():
    query = TrafficQuery.build()


def test_timestamp_conversion():
    start_date = datetime.strptime('2021-11-05', '%Y-%m-%d').replace(tzinfo=timezone.utc)
    start_time_seconds = start_date.timestamp()
    end_date = datetime.strptime('2021-11-12', '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end_time_milliseconds = end_date.timestamp() * 1000
    query = TrafficQuery(start_date=start_time_seconds, end_date=end_time_milliseconds, policy_decisions=["unknown"])
    assert query.start_date == '2021-11-05T00:00:00Z'
    assert query.end_date == '2021-11-12T00:00:00Z'
