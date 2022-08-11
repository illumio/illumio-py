from illumio import PolicyComputeEngine


def test_pce_connection(pce: PolicyComputeEngine):
    assert pce.check_connection()


def test_invalid_org_id(pce: PolicyComputeEngine):
    # since pce is a session fixture, store the original id
    # to reset after we test the failed connection request
    configured_org_id = pce.org_id
    pce.org_id = 999
    assert not pce.check_connection()
    pce.org_id = configured_org_id
