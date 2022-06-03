import pytest

from illumio.util import (
    convert_draft_href_to_active,
    convert_protocol,
    ACTIVE
)

from helpers import random_string


@pytest.mark.parametrize(
    "api_name,sec_policy_object", [
        (
            'ip_lists',
            {
                'description': 'Test IP List provisioning',
                'ip_ranges': [{'from_ip': '10.0.0.0/8'}],
            }
        ),
        (
            'label_groups',
            {
                'key': 'env',
                'description': 'Created by illumio python library integration tests',
                'labels': []
            }
        ),
        (
            'services',
            {
                'description': 'Test service provisioning',
                'service_ports': [{'port': 3306, 'proto': convert_protocol('tcp')}]
            }
        ),
        (
            'rule_sets',
            {
                'description': 'Test rule set provisioning',
                'enabled': True,
                'scopes': []
            }
        )
    ]
)
def test_provision_object(pce, api_name, sec_policy_object, session_identifier, request):
    identifier = random_string()
    api = getattr(pce, api_name)
    sec_policy_object.update({
        'name': '{}-{}'.format(session_identifier, identifier),
        'external_data_set': session_identifier,
        'external_data_reference': identifier
    })
    policy_object = api.create(sec_policy_object)
    pce.provision_policy_changes(
        change_description='Test {} object provisioning'.format(api_name),
        hrefs=[policy_object.href]
    )

    def _teardown():
        api.delete(policy_object.href)
        pce.provision_policy_changes(
            change_description='Remove provisioned {} object'.format(api_name),
            hrefs=[policy_object.href]
        )

    request.addfinalizer(_teardown)

    policy_objects = api.get(params={'name': session_identifier}, policy_version=ACTIVE)
    assert len(policy_objects) == 1 and policy_objects[0].href == convert_draft_href_to_active(policy_object.href)
