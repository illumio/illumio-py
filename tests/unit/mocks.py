import json
import re
from copy import copy
from random import randint
from typing import Any
from urllib.parse import unquote_plus
from uuid import uuid4

from illumio.util import ACTIVE, DRAFT


def _gen_uuid():
    return uuid4()


def _gen_sid():
    # see https://docs.microsoft.com/en-US/windows/security/identity-protection/access-control/security-identifiers
    Y = '-'.join([str(randint(1, 9999999999)) for _ in range(randint(1, 5))])
    return 'S-1-{}-{}-{}'.format(randint(1, 5), randint(1, 99), Y)


def _id_seq_generator():
    next_id = 500
    while True:
        yield next_id
        next_id += 1

_id_sequence = _id_seq_generator()


def _gen_int_id():
    return next(_id_sequence)

OBJECT_TYPE_REF_MAP = {
    'container_clusters': _gen_uuid,
    'container_workload_profiles': _gen_uuid,
    'enforcement_boundaries': _gen_int_id,
    'events': _gen_uuid,
    'ip_lists': _gen_int_id,
    'label_groups': _gen_uuid,
    'labels': _gen_int_id,
    'pairing_profiles': _gen_int_id,
    'rule_sets': _gen_int_id,
    'sec_rules': _gen_int_id,
    'security_principals': _gen_sid,
    'service_bindings': _gen_int_id,
    'services': _gen_int_id,
    'users': _gen_int_id,
    'vens': _gen_uuid,
    'virtual_services': _gen_uuid,
    'workloads': _gen_uuid
}


class PCEObjectMock(object):
    """
    Base class for PCE object mocks
    """
    base_pattern = '^/api/v2(?:/orgs/\d+)?(?:/sec_policy/(?:draft|active))?/([a-zA-Z_\-]+)'
    href_pattern = '^/api/v2((?:/orgs/\d+)?(?:/sec_policy/(?:draft|active))?(?:/[a-zA-Z_\-]+/[a-zA-Z0-9\-]+)+)$'

    def __init__(self) -> None:
        self.mock_objects = []

    def add_mock_objects(self, mock_objects):
        self.mock_objects += mock_objects

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
                if key not in o:
                    continue
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
                elif o[key] is None:
                    match = False
                else:
                    try:
                        match = value in o[key]  # partial match
                    except TypeError:
                        # need exact match for some types
                        # boolean values need to be cast to str to compare
                        match = (value == o[key]) or (str(value) == str(o[key]))
            if match:
                matching_objects.append(o)
        return matching_objects

    def _object_sieve(self, path):
        if '/sec_policy/' in path:
            if '/{}/'.format(ACTIVE) in path:
                return [o for o in self.mock_objects if ACTIVE in o['href']]
            return [o for o in self.mock_objects if DRAFT in o['href']]
        return self.mock_objects

    def create_mock_object(self, path, body):
        pattern = re.compile(self.base_pattern)
        match = re.match(pattern, path)
        if not match:
            raise Exception("Invalid path: {}".format(path))
        object_type = match.group(1)
        href = '/{}/{}'.format(path.split('/api/v2/')[-1], OBJECT_TYPE_REF_MAP[object_type]())
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
                    for k, v in body.items():
                        o[k] = v
                    return
            raise Exception("Attempting to update invalid or missing object")
        raise Exception("Invalid HREF passed to update_mock_object")

    def delete_mock_object(self, path):
        href_capture_pattern = re.compile(self.href_pattern)
        match = re.match(href_capture_pattern, path)
        if match:
            _mock_objects = copy(self.mock_objects)
            for o in _mock_objects:
                if match.group(1) == o['href']:
                    self.mock_objects.remove(o)
                    return
            raise Exception("Attempting to delete invalid or missing object")
        raise Exception("Invalid HREF passed to delete_mock_object")


class MockResponse():
    content = ''
    headers = {'X-Total-Count': 0}

    def raise_for_status(self): pass
    def json(self): return {}
