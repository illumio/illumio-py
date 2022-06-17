import os

import pytest

TEST_DIR = os.path.abspath(os.path.dirname(__file__))


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", default=False, help="run integration tests")


def pytest_configure(config):
    pytest.DATA_DIR = os.path.join(TEST_DIR, 'data')
    config.addinivalue_line("markers", "integration: mark integration tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        return
    integration_skip_marker = pytest.mark.skip(reason="use --integration marker to run")
    for item in items:
        filename = str(item.fspath).split(os.path.sep)[-1]
        if "integration" in item.keywords or filename.startswith('test_intg'):
            item.add_marker(integration_skip_marker)
