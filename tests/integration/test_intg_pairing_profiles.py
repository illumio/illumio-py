import pytest

from illumio.util import EnforcementMode, VisibilityLevel
from illumio.workloads import PairingProfile

from helpers import random_string


@pytest.fixture
def pairing_profile(pce, session_identifier, env_label):
    identifier = random_string()
    pairing_profile = pce.pairing_profiles.create(
        PairingProfile(
            name='{}-PP-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            enabled=True,
            # agent_software_release: str = None
            enforcement_mode=EnforcementMode.VISIBILITY_ONLY.value,
            enforcement_mode_lock=True,
            visibility_level=VisibilityLevel.FLOW_SUMMARY.value,
            visibility_level_lock=True,
            allowed_uses_per_key=1,
            key_lifespan='unlimited',
            labels=[env_label],
            role_label_lock=False,
            app_label_lock=False,
            env_label_lock=True,
            loc_label_lock=False,
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield pairing_profile
    pce.pairing_profiles.delete(pairing_profile.href)


def test_get_by_reference(pce, pairing_profile):
    profile = pce.pairing_profiles.get_by_reference(pairing_profile.href)
    assert profile.href == pairing_profile.href


def test_get_by_partial_name(pce, session_identifier, pairing_profile):
    pairing_profiles = pce.pairing_profiles.get(params={'name': session_identifier})
    assert len(pairing_profiles) == 1


def test_update_pairing_profile(pce, pairing_profile):
    pce.pairing_profiles.update(pairing_profile.href, {
        'enforcement_mode': 'selective'
    })
    profile = pce.pairing_profiles.get_by_reference(pairing_profile.href)
    assert pairing_profile.href == profile.href
    assert profile.enforcement_mode == 'selective'
