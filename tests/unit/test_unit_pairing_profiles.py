import json
import os
import re
from typing import List

import pytest

from illumio.workloads import PairingProfile
from illumio.util import EnforcementMode, VisibilityLevel

MOCK_PAIRING_PROFILES = os.path.join(pytest.DATA_DIR, 'pairing_profiles.json')
MOCK_PAIRING_KEY = os.path.join(pytest.DATA_DIR, 'pairing_key.json')


@pytest.fixture(scope='module')
def pairing_profiles() -> List[dict]:
    with open(MOCK_PAIRING_PROFILES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def mock_pairing_key() -> dict:
    with open(MOCK_PAIRING_KEY, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def pairing_profiles_mock(pce_object_mock, pairing_profiles):
    pce_object_mock.add_mock_objects(pairing_profiles)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback, mock_pairing_key):
    profile_pattern = re.compile('/pairing_profiles')
    requests_mock.register_uri('GET', profile_pattern, json=get_callback)
    requests_mock.register_uri('POST', profile_pattern, json=post_callback)
    requests_mock.register_uri('PUT', profile_pattern, json=put_callback)
    requests_mock.register_uri('DELETE', profile_pattern, json=delete_callback)

    key_pattern = re.compile('/pairing_key')
    requests_mock.register_uri('POST', key_pattern, json=mock_pairing_key)


@pytest.mark.parametrize(
    "key_lifespan,expected", [
        ('unlimited', 'unlimited'),
        (60, 60),
        ('60', 60)
    ]
)
def test_encoded_key_lifespan_value(key_lifespan, expected):
    profile = PairingProfile(
        name='PP-TEST',
        key_lifespan=key_lifespan
    )
    assert profile._encode()['key_lifespan'] == expected


@pytest.mark.parametrize(
    "allowed_uses_per_key,expected", [
        ('unlimited', 'unlimited'),
        (60, 60),
        ('60', 60)
    ]
)
def test_encoded_allowed_uses_per_key_value(allowed_uses_per_key, expected):
    profile = PairingProfile(
        name='PP-TEST',
        allowed_uses_per_key=allowed_uses_per_key
    )
    assert profile._encode()['allowed_uses_per_key'] == expected


def test_encoded_enum_values():
    profile = PairingProfile(
        name='PP-TEST',
        enforcement_mode=EnforcementMode.SELECTIVE,
        visibility_level=VisibilityLevel.FLOW_FULL_DETAIL
    )
    encoded_profile = profile._encode()
    assert type(encoded_profile['enforcement_mode']) is str
    assert type(encoded_profile['visibility_level']) is str


def test_get_profiles_by_name(pce):
    pairing_profiles = pce.pairing_profiles.get(params={'name': 'PP-'})
    assert len(pairing_profiles) == 2


def test_get_by_labels(pce):
    params = {'labels': '[["/orgs/1/labels/136"]]'}
    pairing_profiles = pce.pairing_profiles.get(params=params)
    assert len(pairing_profiles) == 2


def test_get_by_multiple_labels(pce):
    params = {'labels': '[["/orgs/1/labels/224","/orgs/1/labels/136"]]'}
    pairing_profiles = pce.pairing_profiles.get(params=params)
    assert len(pairing_profiles) == 1


def test_get_by_distinct_labels(pce):
    params = {'labels': '[["/orgs/1/labels/224"],["/orgs/1/labels/136"]]'}
    pairing_profiles = pce.pairing_profiles.get(params=params)
    assert len(pairing_profiles) == 3


def test_pairing_profile_create(pce):
    pairing_profile = PairingProfile(name='PP-TEST', enabled=True)
    pairing_profile = pce.pairing_profiles.create(pairing_profile)
    pairing_profiles = pce.pairing_profiles.get()
    assert len(pairing_profiles) == 4
    assert pairing_profile.href in [p.href for p in pairing_profiles]


def test_pairing_profile_update(pce):
    test_description = 'Updated test profile'
    pairing_profiles = pce.pairing_profiles.get()
    pairing_profile = pairing_profiles[0]
    pairing_profile.description = test_description
    pce.pairing_profiles.update(pairing_profile.href, pairing_profile)
    pairing_profile = pce.pairing_profiles.get_by_reference(pairing_profile.href)
    assert pairing_profile.description == test_description


def test_pairing_key_generation(pce, mock_pairing_key):
    pairing_profiles = pce.pairing_profiles.get()
    pairing_key = pce.generate_pairing_key(pairing_profiles[0].href)
    assert pairing_key == mock_pairing_key.get('activation_code')
