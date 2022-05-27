import json
import os
import re

import pytest

from illumio.workloads import PairingProfile

MOCK_PAIRING_PROFILES = os.path.join(pytest.DATA_DIR, 'pairing_profiles.json')
MOCK_PAIRING_KEY = os.path.join(pytest.DATA_DIR, 'pairing_key.json')


@pytest.fixture(scope='module')
def pairing_profiles() -> dict:
    with open(MOCK_PAIRING_PROFILES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def mock_pairing_key() -> dict:
    with open(MOCK_PAIRING_KEY, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def pairing_profiles_mock(PceObjectMock, pairing_profiles):
    yield PceObjectMock(pairing_profiles)


@pytest.fixture(scope='module')
def get_callback(pairing_profiles_mock):
    def _callback_fn(request, context):
        return pairing_profiles_mock.get_mock_objects(request.path_url)
    return _callback_fn


@pytest.fixture(scope='module')
def post_callback(pairing_profiles_mock):
    def _callback_fn(request, context):
        json_body = json.loads(request.body.decode('utf-8'))
        return pairing_profiles_mock.create_mock_object(request.path_url, json_body)
    return _callback_fn


@pytest.fixture(scope='module')
def put_callback(pairing_profiles_mock):
    def _callback_fn(request, context):
        print(request.body.decode('utf-8'))
        json_body = json.loads(request.body.decode('utf-8'))
        print(json_body)
        return pairing_profiles_mock.update_mock_object(request.path_url, json_body)
    return _callback_fn


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, mock_pairing_key):
    profile_pattern = re.compile('/pairing_profile')
    requests_mock.register_uri('GET', profile_pattern, json=get_callback)
    requests_mock.register_uri('POST', profile_pattern, json=post_callback)
    requests_mock.register_uri('PUT', profile_pattern, json=put_callback)

    key_pattern = re.compile('/pairing_key')
    requests_mock.register_uri('POST', key_pattern, json=mock_pairing_key)


def test_get_profiles_by_name(pce):
    pairing_profiles = pce.get_pairing_profiles(params={'name': 'PP-'})
    assert len(pairing_profiles) == 2


def test_get_by_labels(pce):
    params = {'labels': '[["/orgs/{}/labels/136"]]'.format(pce.org_id)}
    pairing_profiles = pce.get_pairing_profiles(params=params)
    assert len(pairing_profiles) == 2


def test_get_by_multiple_labels(pce):
    params = {'labels': '[["/orgs/{0}/labels/224","/orgs/{0}/labels/136"]]'.format(pce.org_id)}
    pairing_profiles = pce.get_pairing_profiles(params=params)
    assert len(pairing_profiles) == 1


def test_get_by_distinct_labels(pce):
    params = {'labels': '[["/orgs/{0}/labels/224"],["/orgs/{0}/labels/136"]]'.format(pce.org_id)}
    pairing_profiles = pce.get_pairing_profiles(params=params)
    assert len(pairing_profiles) == 3


def test_pairing_profile_create(pce):
    pairing_profile = PairingProfile(name='PP-TEST', enabled=True)
    pairing_profile = pce.create_pairing_profile(pairing_profile)
    pairing_profiles = pce.get_pairing_profiles()
    assert len(pairing_profiles) == 4
    assert pairing_profile.href in [p.href for p in pairing_profiles]


def test_pairing_profile_update(pce):
    test_description = 'Updated test profile'
    pairing_profiles = pce.get_pairing_profiles()
    pairing_profile = pairing_profiles[0]
    pairing_profile.description = test_description
    pce.update_pairing_profile(pairing_profile.href, pairing_profile)
    pairing_profile = pce.get_pairing_profile(pairing_profile.href)
    assert pairing_profile.description == test_description


def test_pairing_key_generation(pce, mock_pairing_key):
    pairing_profiles = pce.get_pairing_profiles()
    pairing_key = pce.generate_pairing_key(pairing_profiles[0].href)
    assert pairing_key == mock_pairing_key.get('activation_code')
