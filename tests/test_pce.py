def test_failed_connection_check(pce):
    assert pce.check_connection() == False
