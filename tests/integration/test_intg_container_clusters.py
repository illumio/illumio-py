def test_get_by_reference(pce, container_cluster):
    cluster = pce.container_clusters.get_by_reference(container_cluster.href)
    del container_cluster.container_cluster_token  # pop the token for the comparison
    assert cluster.href == container_cluster.href


def test_get_by_partial_name(pce, session_identifier, container_cluster):
    container_clusters = pce.container_clusters.get(params={'name': session_identifier})
    assert len(container_clusters) == 1


def test_update_container_cluster(pce, container_cluster):
    updated_description = 'Updated description'
    pce.container_clusters.update(container_cluster.href, {
        'description': updated_description
    })
    cluster = pce.container_clusters.get_by_reference(container_cluster.href)
    assert container_cluster.href == cluster.href
    assert cluster.description == updated_description
