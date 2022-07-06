import pytest

from illumio.infrastructure import ContainerWorkloadProfile, LabelRestriction
from illumio.util import EnforcementMode

from helpers import random_string


@pytest.fixture
def container_workload_profile(pce, session_identifier, container_cluster, env_label, loc_label):
    identifier = random_string()
    container_workload_profile = ContainerWorkloadProfile(
        name='{}-{}'.format(session_identifier, identifier),
        description='Created by illumio python library integration tests',
        managed=True,
        assign_labels=[env_label, loc_label],
        enforcement_mode=EnforcementMode.VISIBILITY_ONLY
    )
    container_workload_profile = pce.container_workload_profiles.create(
        container_workload_profile,
        parent=container_cluster.href
    )
    yield container_workload_profile
    pce.container_workload_profiles.delete(container_workload_profile)


def test_get_by_reference(pce, container_workload_profile):
    workload_profile = pce.container_workload_profiles.get_by_reference(container_workload_profile)
    assert workload_profile.href == container_workload_profile.href


def test_get_from_container_cluster(pce, container_cluster, container_workload_profile):
    container_workload_profiles = pce.container_workload_profiles.get(parent=container_cluster.href)
    assert len(container_workload_profiles) == 2  # every cluster has a Default profile


def test_update_container_workload_profile(pce, container_workload_profile, app_label, env_label, loc_label):
    label_restrictions = [
        LabelRestriction(key='app', restriction=[app_label]),
        LabelRestriction(key='env', assignment=env_label),
        LabelRestriction(key='loc', assignment=loc_label),
    ]
    pce.container_workload_profiles.update(container_workload_profile, {'labels': label_restrictions})
    updated_container_workload_profile = pce.container_workload_profiles.get_by_reference(container_workload_profile)
    assert len(updated_container_workload_profile.labels) == 3
