from illumio import PolicyComputeEngine


def test_pce_connection(pce: PolicyComputeEngine):
    assert pce.check_connection()
