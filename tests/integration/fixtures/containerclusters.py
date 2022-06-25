import pytest

from illumio.infrastructure import ContainerCluster

from helpers import random_string


@pytest.fixture
def container_cluster(pce, session_identifier):
    identifier = random_string()
    container_cluster = pce.container_clusters.create(
        ContainerCluster(
            name='{}-CC-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests'
        )
    )
    yield container_cluster
    pce.container_clusters.delete(container_cluster.href)

__all__ = ['container_cluster']
