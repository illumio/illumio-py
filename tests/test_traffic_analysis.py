import json
import os
import re
from datetime import datetime, timezone
from typing import List

import pytest
from requests_mock import ANY

from illumio import IllumioException
from illumio.explorer import TrafficQuery, TrafficQueryFilterBlock, TrafficFlow

MOCK_TRAFFIC_QUERY = os.path.join(pytest.DATA_DIR, 'traffic_query.json')
MOCK_TRAFFIC_FLOWS = os.path.join(pytest.DATA_DIR, 'traffic_query_response.json')


@pytest.fixture(scope='module')
def traffic_query() -> TrafficQuery:
    with open(MOCK_TRAFFIC_QUERY, 'r') as f:
        yield TrafficQuery.from_json(f.read())


@pytest.fixture(scope='module')
def traffic_flows() -> List[TrafficFlow]:
    with open(MOCK_TRAFFIC_FLOWS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def traffic_flows_mock(pce_object_mock, traffic_flows):
    pce_object_mock.add_mock_objects(traffic_flows)


@pytest.fixture
def traffic_query_callback(pce_object_mock):
    def _callback_fn(request, context):
        return pce_object_mock.get_mock_objects(request.path_url)
    return _callback_fn


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, traffic_query_callback):
    pattern = re.compile('/traffic_flows/traffic_analysis_queries')
    requests_mock.register_uri('POST', pattern, json=traffic_query_callback)


def test_query_structure(traffic_query):
    assert type(traffic_query.sources) is TrafficQueryFilterBlock


def test_traffic_query(pce, traffic_query):
    traffic_flows = pce.get_traffic_flows(traffic_query)
    assert len(traffic_flows) > 0
    assert traffic_flows[0].src is not None


def test_invalid_policy_decision():
    with pytest.raises(IllumioException):
        TrafficQuery(start_date='2021-11-05', end_date='2021-11-12', policy_decisions=["invalid_policy_decision"])


def test_timestamp_conversion():
    start_date = datetime.strptime('2021-11-05', '%Y-%m-%d').replace(tzinfo=timezone.utc)
    start_time_seconds = start_date.timestamp()
    end_date = datetime.strptime('2021-11-12', '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end_time_milliseconds = end_date.timestamp() * 1000
    query = TrafficQuery(start_date=start_time_seconds, end_date=end_time_milliseconds, policy_decisions=["unknown"])
    assert query.start_date == '2021-11-05T00:00:00Z'
    assert query.end_date == '2021-11-12T00:00:00Z'
