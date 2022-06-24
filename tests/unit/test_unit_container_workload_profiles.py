import json
import os
import re
from typing import List

import pytest

from illumio.infrastructure import ContainerWorkloadProfile
from illumio.util import EnforcementMode

CONTAINER_WORKLOAD_PROFILES = os.path.join(pytest.DATA_DIR, 'container_workload_profiles.json')
CONTAINER_CLUSTER_HREF = '/orgs/1/container_clusters/f5bef182-8c55-4219-b35b-0a50b707e434'


@pytest.fixture(scope='module')
def container_workload_profiles() -> List[dict]:
    with open(CONTAINER_WORKLOAD_PROFILES, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(autouse=True)
def container_clusters_mock(pce_object_mock, container_workload_profiles):
    pce_object_mock.add_mock_objects(container_workload_profiles)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/container_workload_profiles')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


def test_get_workload_profiles_by_cluster(pce):
    workload_profiles = pce.container_workload_profiles.get(parent=CONTAINER_CLUSTER_HREF)
    assert len(workload_profiles) == 9


def test_get_managed_workload_profiles(pce):
    workload_profiles = pce.container_workload_profiles.get(params={'managed': True}, parent=CONTAINER_CLUSTER_HREF)
    assert len(workload_profiles) == 2


def test_add_workload_profile_to_cluster(pce):
    workload_profile = ContainerWorkloadProfile(namespace='illumio-system')
    workload_profile = pce.container_workload_profiles.create(workload_profile, parent=CONTAINER_CLUSTER_HREF)
    workload_profiles = pce.container_workload_profiles.get(parent=CONTAINER_CLUSTER_HREF)
    assert workload_profile.href in [profile.href for profile in workload_profiles]


def test_update_workload_profile(pce):
    workload_profile = pce.container_workload_profiles.get(params={'namespace': 'illumio-system', 'max_results': 1})[0]
    pce.container_workload_profiles.update(workload_profile.href, {'enforcement_mode': EnforcementMode.FULL})
    updated_workload_profile = pce.container_workload_profiles.get_by_reference(workload_profile.href)
    assert updated_workload_profile.enforcement_mode == EnforcementMode.FULL.value

