import pytest
from illumio.policyobjects import LabelGroup
from helpers import random_string

@pytest.fixture
def nested_label_group_set(pce, session_identifier):
    """
    Setup fixture to create a child Label Group and a parent Label Group
    that contains the child.
    """
    identifier_child = random_string()
    child_lg = pce.label_groups.create(
        LabelGroup(
            key='app',
            name='{}-CHILD-{}'.format(session_identifier, identifier_child),
            external_data_set=session_identifier,
            external_data_reference=identifier_child
        )
    )
    
    identifier_parent = random_string()
    parent_lg = pce.label_groups.create(
        LabelGroup(
            key='app',
            name='{}-PARENT-{}'.format(session_identifier, identifier_parent),
            sub_groups=[child_lg], # This is the key part that tests the bug fix
            external_data_set=session_identifier,
            external_data_reference=identifier_parent
        )
    )
    
    yield parent_lg, child_lg
    
    # Teardown: delete parent first, then child
    pce.label_groups.delete(parent_lg.href)
    pce.label_groups.delete(child_lg.href)

@pytest.mark.integration
def test_nested_label_group_retrieval(pce, nested_label_group_set):
    """
    Verifies that nested sub-groups are correctly fetched and deserialized
    as LabelGroup objects when communicating with a real PCE.
    """
    parent, child = nested_label_group_set
    
    # Fetch the parent by reference
    fetched_parent = pce.label_groups.get_by_reference(parent.href)
    
    assert fetched_parent.name == parent.name
    assert len(fetched_parent.sub_groups) == 1
    
    # Verify the nested child is correctly deserialized as a LabelGroup
    fetched_child = fetched_parent.sub_groups[0]
    assert isinstance(fetched_child, LabelGroup)
    assert fetched_child.name == child.name
    assert fetched_child.href == child.href
