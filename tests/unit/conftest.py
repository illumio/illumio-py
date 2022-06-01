import json

import pytest

from illumio import PolicyComputeEngine
from mocks import PCEObjectMock


@pytest.fixture(scope='session')
def pce():
    return PolicyComputeEngine('test.pce.com')


@pytest.fixture
def pce_object_mock():
    yield PCEObjectMock()


@pytest.fixture
def get_callback(pce_object_mock):
    def _callback_fn(request, context):
        context.headers['X-Total-Count'] = str(len(pce_object_mock.mock_objects))
        return pce_object_mock.get_mock_objects(request.path_url)
    return _callback_fn


@pytest.fixture
def post_callback(pce_object_mock):
    def _callback_fn(request, context):
        json_body = json.loads(request.body.decode('utf-8'))
        return pce_object_mock.create_mock_object(request.path_url, json_body)
    return _callback_fn


@pytest.fixture
def put_callback(pce_object_mock):
    def _callback_fn(request, context):
        json_body = json.loads(request.body.decode('utf-8'))
        pce_object_mock.update_mock_object(request.path_url, json_body)
    return _callback_fn


@pytest.fixture
def delete_callback(pce_object_mock):
    def _callback_fn(request, context):
        pce_object_mock.delete_mock_object(request.path_url)
    return _callback_fn
