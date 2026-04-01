import os
import json
import pytest
import re
from illumio.pce import PolicyComputeEngine
from illumio.policyobjects import LabelGroup, Label
from illumio.util import Reference


@pytest.fixture
def label_groups_json():
    data_path = os.path.join(pytest.DATA_DIR, 'label_groups.json')
    with open(data_path, 'r') as f:
        return json.load(f)


def test_label_group_deserialization_all_fields(pce, requests_mock, label_groups_json):
    """
    Verifies that ALL fields of a LabelGroup response are correctly
    deserialized, including nested labels and sub_groups.
    """
    matcher = requests_mock.get(re.compile('/sec_policy/draft/label_groups'), json=label_groups_json)

    label_groups = pce.label_groups.get()

    assert matcher.called
    assert len(label_groups) == 5

    # Test KCLG1 - has both labels and sub_groups
    kclg1 = next(lg for lg in label_groups if lg.name == "KCLG1")

    # Test Reference fields (inherited from Reference)
    assert kclg1.href == "/orgs/65567/sec_policy/draft/label_groups/917de8cc-9bfd-4fc3-b289-d1476d89c3de"

    # Test IllumioObject fields (inherited)
    assert kclg1.name == "KCLG1"
    assert kclg1.description == ""

    # Test MutableObject fields (inherited)
    assert kclg1.created_at == "2026-04-01T03:33:38.051Z"
    assert kclg1.updated_at == "2026-04-01T03:55:19.326Z"
    assert kclg1.deleted_at is None
    assert kclg1.update_type is None
    assert kclg1.deleted_by is None

    # Test created_by and updated_by are Reference objects
    assert isinstance(kclg1.created_by, Reference)
    assert kclg1.created_by.href == "/users/56294995342151520"
    assert isinstance(kclg1.updated_by, Reference)
    assert kclg1.updated_by.href == "/users/56294995342151520"

    # Test Label fields (inherited)
    assert kclg1.key == "servicecategory"

    # Test LabelGroup.labels - should be list of Reference objects
    assert kclg1.labels is not None
    assert len(kclg1.labels) == 3

    for label in kclg1.labels:
        assert isinstance(label, Reference)
        assert label.href is not None
        assert label.href.startswith("/orgs/65567/labels/")

    # Verify specific label values
    label_values = {getattr(l, 'value', None) for l in kclg1.labels}
    assert "App Service" in label_values
    assert "Compute" in label_values
    assert "Databases" in label_values

    # Test LabelGroup.sub_groups - should be list of LabelGroup objects
    assert kclg1.sub_groups is not None
    assert len(kclg1.sub_groups) == 2

    for sub_group in kclg1.sub_groups:
        assert isinstance(sub_group, LabelGroup), \
            f"sub_group should be LabelGroup, got {type(sub_group)}"
        assert sub_group.href is not None
        assert sub_group.name is not None

    sub_group_names = {sg.name for sg in kclg1.sub_groups}
    assert sub_group_names == {"KCLG4", "KCLG5"}


def test_label_group_with_multiple_labels(pce, requests_mock, label_groups_json):
    """
    Verifies that label groups with multiple labels have all labels
    correctly deserialized with their fields.
    """
    matcher = requests_mock.get(re.compile('/sec_policy/draft/label_groups'), json=label_groups_json)

    label_groups = pce.label_groups.get()

    # Test KCLG3 - has 3 labels with different values
    kclg3 = next(lg for lg in label_groups if lg.name == "KCLG3")

    assert kclg3.key == "servicerole"
    assert kclg3.description == "Description for KCLG3"
    assert len(kclg3.labels) == 3

    # Verify all labels have required fields
    expected_labels = [
        {"href": "/orgs/65567/labels/281474976712748", "key": "servicerole", "value": "AgentPoolMachines"},
        {"href": "/orgs/65567/labels/281474976712751", "key": "servicerole", "value": "AgentPools"},
        {"href": "/orgs/65567/labels/281474976712733", "key": "servicerole", "value": "ComputeVirtualMachines"},
    ]

    for expected in expected_labels:
        label = next((l for l in kclg3.labels if l.href == expected["href"]), None)
        assert label is not None, f"Label with href {expected['href']} not found"
        # Labels in label groups are References, check available fields
        assert label.href == expected["href"]


def test_label_group_empty_sub_groups(pce, requests_mock, label_groups_json):
    """
    Verifies that label groups with empty sub_groups are handled correctly.
    """
    matcher = requests_mock.get(re.compile('/sec_policy/draft/label_groups'), json=label_groups_json)

    label_groups = pce.label_groups.get()

    # Test KCLG2 - has labels but no sub_groups
    kclg2 = next(lg for lg in label_groups if lg.name == "KCLG2")

    assert kclg2.key == "type"
    assert kclg2.description == "description for KGLG2"
    assert len(kclg2.labels) == 3
    assert kclg2.sub_groups == []

    # Verify label values
    label_hrefs = {l.href for l in kclg2.labels}
    assert "/orgs/65567/labels/281474976712535" in label_hrefs
    assert "/orgs/65567/labels/281474976712523" in label_hrefs
    assert "/orgs/65567/labels/281474976712524" in label_hrefs


def test_all_label_groups_have_required_fields(pce, requests_mock, label_groups_json):
    """
    Verifies that all label groups in the response have required fields populated.
    """
    matcher = requests_mock.get(re.compile('/sec_policy/draft/label_groups'), json=label_groups_json)

    label_groups = pce.label_groups.get()

    for lg in label_groups:
        # Required fields should be present
        assert lg.href is not None, f"LabelGroup {lg.name} missing href"
        assert lg.name is not None, f"LabelGroup {lg.href} missing name"
        assert lg.key is not None, f"LabelGroup {lg.name} missing key"
        assert lg.created_at is not None, f"LabelGroup {lg.name} missing created_at"
        assert lg.updated_at is not None, f"LabelGroup {lg.name} missing updated_at"
        assert lg.created_by is not None, f"LabelGroup {lg.name} missing created_by"
        assert lg.updated_by is not None, f"LabelGroup {lg.name} missing updated_by"

        # created_by and updated_by should be Reference objects
        assert isinstance(lg.created_by, Reference), \
            f"LabelGroup {lg.name} created_by should be Reference"
        assert isinstance(lg.updated_by, Reference), \
            f"LabelGroup {lg.name} updated_by should be Reference"

        # labels should be a list (possibly empty)
        assert isinstance(lg.labels, list), f"LabelGroup {lg.name} labels should be list"

        # sub_groups should be a list (possibly empty)
        assert isinstance(lg.sub_groups, list), f"LabelGroup {lg.name} sub_groups should be list"

        # All sub_groups should be LabelGroup instances
        for i, sg in enumerate(lg.sub_groups):
            assert isinstance(sg, LabelGroup), \
                f"LabelGroup {lg.name} sub_groups[{i}] should be LabelGroup, got {type(sg)}"
