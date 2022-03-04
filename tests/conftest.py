import os
import re
from urllib.parse import unquote_plus

import pytest

from illumio import PolicyComputeEngine

TEST_DIR = os.path.abspath(os.path.dirname(__file__))


def pytest_configure():
    pytest.DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.fixture(scope='session')
def pce():
    return PolicyComputeEngine('test.pce.com', port=443)


class _PolicyUtil:
    """
    Helper functions for policy object test suites.
    """
    def __init__(self, draft_objects, active_objects) -> None:
        self.draft_objects = draft_objects
        self.active_objects = active_objects

    def get_mock_objects(self, path):
        pattern = re.compile('^/api/v2/orgs/\d+/sec_policy/(draft|active)/')
        match = re.match(pattern, path)
        if not match:
            raise Exception("Invalid path: {}".format(path))
        objects = self.draft_objects if match.group(1) == 'draft' else self.active_objects
        json = self._get_policy_object_by_href(path, objects)
        if json is None:
            json = self._get_matching_objects(path, objects)
        return json

    def _get_policy_object_by_href(self, path, objects):
        href_capture_pattern = re.compile('^/api/v2(/orgs/\d+/sec_policy/(draft|active)/[a-zA-Z_\-]+/[a-zA-Z0-9\-]+)$')
        match = re.match(href_capture_pattern, path)
        if match:
            for o in objects:
                if match.group(1) == o['href']:
                    return o
            return {}
        return None

    def _get_matching_objects(self, path, objects):
        url_pattern = re.compile('^/api/v2/orgs/\d+/sec_policy/(draft|active)/[a-zA-Z_\-]+')
        match = re.match(url_pattern, path)
        if match:
            matching_objects = []
            for o in objects:
                match = True
                query_pattern = re.compile('([a-zA-Z0-9_\-\+%]+)=([a-zA-Z0-9_\-\+%\.\\\/~]+)')
                for param_match in re.finditer(query_pattern, path):
                    key, value = param_match.group(1), unquote_plus(param_match.group(2), encoding='utf-8')
                    if value not in o[key]:
                        match = False
                if match:
                    matching_objects.append(o)
            return matching_objects
        return None


@pytest.fixture(scope='session')
def PolicyUtil():
    return _PolicyUtil
