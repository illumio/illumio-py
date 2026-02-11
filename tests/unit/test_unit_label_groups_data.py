import os
import json
import pytest
import requests_mock
from illumio.pce import PolicyComputeEngine
from illumio.policyobjects import LabelGroup

import re

@pytest.fixture
def label_groups_json():
    data_path = os.path.join(pytest.DATA_DIR, 'label_groups.json')
    with open(data_path, 'r') as f:
        return json.load(f)

def test_label_group_deserialization_from_data(pce, requests_mock, label_groups_json):
    """
    Verifies that a Label Group response with nested sub-groups is correctly
    deserialized into LabelGroup objects using real data.
    """
    matcher = requests_mock.get(re.compile('/sec_policy/draft/label_groups'), json=label_groups_json)
    
    label_groups = pce.label_groups.get()
    
    assert matcher.called
    assert len(label_groups) == 2
    
    parent_lg = label_groups[0]
    assert parent_lg.name == "WindowsApplications"
    assert parent_lg.key == "app"
    
    assert len(parent_lg.sub_groups) == 1
    sub_group = parent_lg.sub_groups[0]
    
    assert isinstance(sub_group, LabelGroup)
    assert sub_group.name == "WindowsAppsFromMicrosoft"
    assert sub_group.href == "/orgs/1/sec_policy/draft/label_groups/77ae18f5-b4cf-4404-a606-925114dec0f1"
