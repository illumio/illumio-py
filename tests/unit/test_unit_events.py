import json
import os
import re
from typing import List

import pytest

from illumio import Event

EVENTS = os.path.join(pytest.DATA_DIR, 'events.json')


@pytest.fixture(scope='module')
def events() -> List[dict]:
    with open(EVENTS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def events_mock(pce_object_mock, events):
    pce_object_mock.add_mock_objects(events)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback):
    pattern = re.compile('/events')
    requests_mock.register_uri('GET', pattern, json=get_callback)


@pytest.fixture()
def mock_event(pce) -> Event:
    yield pce.events.get_by_reference("/orgs/1/events/a066c6ec-4d4a-4c51-bf46-9a20add3bcac")


def test_get_by_hostname(pce, mock_event):
    event = pce.events.get(params={'event_type': 'user.login'})[0]
    assert event == mock_event
