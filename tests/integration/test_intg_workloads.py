from illumio.workloads import Workload

from helpers import random_string


def test_get_by_reference(pce, workload):
    wl = pce.workloads.get_by_reference(workload.href)
    assert wl.href == workload.href


def test_get_by_partial_name(pce, session_identifier, workload):
    workloads = pce.workloads.get(params={'name': session_identifier})
    assert len(workloads) == 1


def test_get_async(pce, session_identifier, workload):
    workloads = pce.workloads.get_async(params={'name': session_identifier})
    assert len(workloads) == 1


def test_update_workload(pce, workload):
    pce.workloads.update(
        workload.href,
        {
            'public_ip': '127.0.0.1',
            'description': 'Integration test update. Disable rule set.'
        }
    )
    wl = pce.workloads.get_by_reference(workload.href)
    assert wl.public_ip == '127.0.0.1'


def test_bulk_create(pce, session_identifier, request):
    id_1 = random_string()
    id_2 = random_string()

    hostname_1 = '{}.{}'.format(session_identifier, id_1)
    hostname_2 = '{}.{}'.format(session_identifier, id_2)

    workloads = [
        Workload(
            name=hostname_1,
            hostname=hostname_1,
            # TODO
            description='Created by illumio python library integration tests',
            external_data_set=session_identifier,
            external_data_reference=id_1
        ),
        {
            'name': hostname_2,
            'hostname': hostname_2,
            'description': 'Created by illumio python library integration tests',
            'external_data_set': session_identifier,
            'external_data_reference': id_2
        }
    ]

    results = pce.workloads.bulk_create(workloads)

    def _teardown():
        pce.workloads.bulk_delete([result['href'] for result in results])

    request.addfinalizer(_teardown)


    for result in results:
        assert not result['errors']
    workloads = pce.workloads.get(params={'external_data_set': session_identifier})
    assert len(workloads) == 2


def test_bulk_update(pce, session_identifier, workload, request):
    identifier = random_string()
    hostname = '{}.{}'.format(session_identifier, identifier)

    new_workload = pce.workloads.create(
        Workload(
            name=hostname,
            hostname=hostname,
            description='Created by illumio python library integration tests',
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )

    def _teardown():
        pce.workloads.delete(new_workload)

    request.addfinalizer(_teardown)

    workloads = [
        {
            'href': wl.href,
            'enforcement_mode': 'selective'
        } for wl in [workload, new_workload]
    ]

    results = pce.workloads.bulk_update(workloads)
    for result in results:
        assert not result['errors']
    workloads = pce.workloads.get(params={'external_data_set': session_identifier})
    for wl in workloads:
        assert wl.enforcement_mode == 'selective'


def test_bulk_delete(pce, session_identifier):
    id_1 = random_string()
    id_2 = random_string()

    hostname_1 = '{}.{}'.format(session_identifier, id_1)
    hostname_2 = '{}.{}'.format(session_identifier, id_2)

    workloads = [
        Workload(
            name=hostname_1,
            hostname=hostname_1,
            # TODO
            description='Created by illumio python library integration tests',
            external_data_set=session_identifier,
            external_data_reference=id_1
        ),
        {
            'name': hostname_2,
            'hostname': hostname_2,
            'description': 'Created by illumio python library integration tests',
            'external_data_set': session_identifier,
            'external_data_reference': id_2
        }
    ]

    created_workloads = []

    for workload in workloads:
        created_workloads.append(pce.workloads.create(workload))

    results = pce.workloads.bulk_delete(created_workloads)
    for result in results:
        assert not result['errors']
    workloads = pce.workloads.get(params={'external_data_set': session_identifier})
    assert len(workloads) == 0
