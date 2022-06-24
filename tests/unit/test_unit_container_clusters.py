import json
import os
import re
from typing import List

import pytest

from illumio.infrastructure import ContainerCluster

CONTAINER_CLUSTERS = os.path.join(pytest.DATA_DIR, 'container_clusters.json')


@pytest.fixture(scope='module')
def container_clusters() -> List[dict]:
    with open(CONTAINER_CLUSTERS, 'r') as f:
        yield json.loads(f.read())


@pytest.fixture(scope='module')
def container_cluster() -> ContainerCluster:
    return ContainerCluster(
        name='CC-TEST',
        description='Test cluster'
    )


@pytest.fixture(autouse=True)
def container_clusters_mock(pce_object_mock, container_clusters):
    pce_object_mock.add_mock_objects(container_clusters)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, get_callback, post_callback, put_callback, delete_callback):
    pattern = re.compile('/container_clusters')
    requests_mock.register_uri('GET', pattern, json=get_callback)
    requests_mock.register_uri('POST', pattern, json=post_callback)
    requests_mock.register_uri('PUT', pattern, json=put_callback)
    requests_mock.register_uri('DELETE', pattern, json=delete_callback)


def test_get_cluster_by_name(pce):
    container_clusters = pce.container_clusters.get(params={'name': 'CC-'})
    assert len(container_clusters) == 2


def test_container_cluster_create(pce, container_cluster):
    container_cluster = pce.container_clusters.create(container_cluster)
    container_clusters = pce.container_clusters.get()
    assert len(container_clusters) == 3
    assert container_cluster.href in [p.href for p in container_clusters]


def test_container_cluster_update(pce):
    test_description = 'Updated test cluster'
    container_clusters = pce.container_clusters.get()
    container_cluster = container_clusters[0]
    container_cluster.description = test_description
    pce.container_clusters.update(container_cluster.href, container_cluster)
    container_cluster = pce.container_clusters.get_by_reference(container_cluster.href)
    assert container_cluster.description == test_description
