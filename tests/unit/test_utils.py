from illumio.util import EnforcementMode


def test_enum_contains():
    assert 'idle' in EnforcementMode
    assert 'invalid_value' not in EnforcementMode
