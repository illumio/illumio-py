from illumio import PolicyComputeEngine


def test_custom_protocol():
    pce = PolicyComputeEngine('http://my.pce.com')
    assert pce.base_url == 'http://my.pce.com:443/api/v2'


def test_invalid_protocol():
    pce = PolicyComputeEngine('ftp://my.pce.com')
    assert pce.base_url == 'https://my.pce.com:443/api/v2'


def test_protocol_parsing():
    pce = PolicyComputeEngine('httpslab.pce.com')
    assert pce.base_url == 'https://httpslab.pce.com:443/api/v2'


def test_path_parsing():
    pce = PolicyComputeEngine('my.pce.com/api/v2')
    assert pce.base_url == 'https://my.pce.com:443/api/v2'


def test_int_org_id():
    pce = PolicyComputeEngine('my.pce.com', org_id=1)
    assert pce.base_url == 'https://my.pce.com:443/api/v2'
