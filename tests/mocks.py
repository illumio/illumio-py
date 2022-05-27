import json
import re
from copy import copy
from urllib.parse import unquote_plus
from typing import Any
from uuid import uuid4

from illumio.util import ACTIVE, DRAFT


def _gen_uuid():
    return uuid4()


def _id_seq_generator():
    next_id = 500
    while True:
        yield next_id
        next_id += 1

_id_sequence = _id_seq_generator()


def _gen_int_id():
    return next(_id_sequence)

OBJECT_TYPE_REF_MAP = {
    'ip_lists': _gen_int_id,
    'rule_sets': _gen_int_id,
    'labels': _gen_int_id,
    'pairing_profiles': _gen_int_id,
    'workloads': _gen_uuid,
    'virtual_services': _gen_uuid
}


class PceObjectMock(object):
    """
    Base class for PCE object mocks
    """
    base_pattern = '^/api/v2/orgs/\d+/([a-zA-Z_\-]+)'
    href_pattern = '^/api/v2(/orgs/\d+/[a-zA-Z_\-]+/[a-zA-Z0-9\-]+)$'

    def __init__(self, mock_objects) -> None:
        self.mock_objects = mock_objects

    def get_mock_objects(self, path) -> Any:
        pattern = re.compile(self.base_pattern)
        match = re.match(pattern, path)
        if not match:
            raise Exception("Invalid path: {}".format(path))
        json = self._get_policy_object_by_href(path)
        if json is None:
            json = self._get_matching_objects(path)
        return json

    def _get_policy_object_by_href(self, path):
        href_capture_pattern = re.compile(self.href_pattern)
        match = re.match(href_capture_pattern, path)
        if match:
            for o in self.mock_objects:
                if match.group(1) == o['href']:
                    return o
            return {}
        return None

    def _get_matching_objects(self, path):
        matching_objects = []
        for o in self._object_sieve(path):
            match = True
            query_pattern = re.compile('([a-zA-Z0-9_\-\+%]+)=([a-zA-Z0-9_\-\+%\.\\\/~]+)')
            for param_match in re.finditer(query_pattern, path):
                key, value = param_match.group(1), unquote_plus(param_match.group(2), encoding='utf-8')
                if key == 'labels':
                    # labels param is a list of lists of label HREFs
                    # example: [["/orgs/1/labels/1", "/orgs/1/labels/2"], ["/orgs/1/labels/3"]]
                    # is equivalent to (1 AND 2) OR 3
                    label_hrefs = [label['href'] for label in o[key]]
                    label_match = False
                    for label_set in json.loads(value):
                        label_set_match = True
                        for label_href in label_set:
                            if label_href not in label_hrefs:
                                label_set_match = False
                        if label_set_match:
                            label_match = True
                            break
                    if not label_match:
                        match = False
                elif value not in o[key]:
                    match = False
            if match:
                matching_objects.append(o)
        return matching_objects

    def _object_sieve(self, path):
        return self.mock_objects

    def create_mock_object(self, path, body):
        pattern = re.compile(self.base_pattern)
        match = re.match(pattern, path)
        if not match:
            raise Exception("Invalid path: {}".format(path))
        object_type = match.group(1)
        href = '{}/{}'.format(path.lstrip('/api/v2'), OBJECT_TYPE_REF_MAP[object_type]())
        body['href'] = href
        self.mock_objects.append(body)
        return body

    def update_mock_object(self, path, body):
        href_capture_pattern = re.compile(self.href_pattern)
        match = re.match(href_capture_pattern, path)
        if match:
            _mock_objects = copy(self.mock_objects)
            for o in _mock_objects:
                if match.group(1) == o['href']:
                    self.mock_objects.remove(o)
                    self.mock_objects.append(body)
                    return body
            raise Exception("Attempting to update invalid or missing object")
        raise Exception("Invalid HREF passed to update_mock_object")


class PolicyObjectMock(PceObjectMock):
    base_pattern = '^/api/v2/orgs/\d+/sec_policy/(?:draft|active)/'
    href_pattern = '^/api/v2(/orgs/\d+/sec_policy/(?:draft|active)/[a-zA-Z_\-]+/[a-zA-Z0-9\-]+)$'

    def _object_sieve(self, path):
        if '/{}/'.format(ACTIVE) in path:
            return [o for o in self.mock_objects if ACTIVE in o['href']]
        return [o for o in self.mock_objects if DRAFT in o['href']]
