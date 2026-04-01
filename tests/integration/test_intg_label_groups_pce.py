import pytest
from illumio.policyobjects import LabelGroup, Label
from illumio.util import Reference
from helpers import random_string


@pytest.fixture
def test_labels(pce, session_identifier):
    """
    Create test labels to be used in label groups.
    """
    labels = []
    for i in range(3):
        identifier = random_string()
        label = pce.labels.create(
            Label(
                key='app',
                value='{}-LABEL-{}-{}'.format(session_identifier, i, identifier),
                external_data_set=session_identifier,
                external_data_reference=identifier
            )
        )
        labels.append(label)

    yield labels

    # Teardown
    for label in labels:
        pce.labels.delete(label.href)


@pytest.fixture
def nested_label_group_set(pce, session_identifier, test_labels):
    """
    Setup fixture to create multiple child Label Groups and a parent Label Group
    that contains them. Tests that ALL sub_groups and labels are correctly deserialized.
    """
    # Create multiple child label groups with descriptions
    children = []
    for i in range(3):
        identifier_child = random_string()
        child_lg = pce.label_groups.create(
            LabelGroup(
                key='app',
                name='{}-CHILD-{}-{}'.format(session_identifier, i, identifier_child),
                description='Child label group {} for integration test'.format(i),
                external_data_set=session_identifier,
                external_data_reference=identifier_child
            )
        )
        children.append(child_lg)

    identifier_parent = random_string()
    parent_lg = pce.label_groups.create(
        LabelGroup(
            key='app',
            name='{}-PARENT-{}'.format(session_identifier, identifier_parent),
            description='Parent label group for integration test',
            labels=test_labels,  # Add labels to the parent
            sub_groups=children,  # Multiple sub_groups to test the fix
            external_data_set=session_identifier,
            external_data_reference=identifier_parent
        )
    )

    yield parent_lg, children, test_labels

    # Teardown: delete parent first, then children
    pce.label_groups.delete(parent_lg.href)
    for child in children:
        pce.label_groups.delete(child.href)


@pytest.mark.integration
def test_label_group_all_fields(pce, nested_label_group_set):
    """
    Verifies that ALL fields of a LabelGroup are correctly populated
    when fetched from a real PCE.
    """
    parent, children, labels = nested_label_group_set

    # Fetch the parent by reference
    fetched = pce.label_groups.get_by_reference(parent.href)

    # Test Reference fields
    assert fetched.href == parent.href
    assert fetched.href.startswith('/orgs/')
    assert '/label_groups/' in fetched.href

    # Test IllumioObject fields
    assert fetched.name == parent.name
    assert fetched.description == 'Parent label group for integration test'
    assert fetched.external_data_set is not None
    assert fetched.external_data_reference is not None

    # Test MutableObject fields
    assert fetched.created_at is not None
    assert fetched.updated_at is not None
    assert isinstance(fetched.created_by, Reference)
    assert fetched.created_by.href is not None
    assert isinstance(fetched.updated_by, Reference)
    assert fetched.updated_by.href is not None

    # Test Label fields
    assert fetched.key == 'app'

    # Test LabelGroup.labels
    assert fetched.labels is not None
    assert len(fetched.labels) == len(labels)
    for label in fetched.labels:
        assert isinstance(label, Reference)
        assert label.href is not None

    # Test LabelGroup.sub_groups
    assert fetched.sub_groups is not None
    assert len(fetched.sub_groups) == len(children)
    for sg in fetched.sub_groups:
        assert isinstance(sg, LabelGroup)
        assert sg.href is not None
        assert sg.name is not None


@pytest.mark.integration
def test_nested_label_group_retrieval(pce, nested_label_group_set):
    """
    Verifies that nested sub-groups are correctly fetched and deserialized
    as LabelGroup objects when communicating with a real PCE.
    """
    parent, children, labels = nested_label_group_set

    # Fetch the parent by reference
    fetched_parent = pce.label_groups.get_by_reference(parent.href)

    assert fetched_parent.name == parent.name
    assert len(fetched_parent.sub_groups) == len(children)

    # Verify ALL nested children are correctly deserialized as LabelGroup
    children_hrefs = {child.href for child in children}
    for i, fetched_child in enumerate(fetched_parent.sub_groups):
        assert isinstance(fetched_child, LabelGroup), \
            f"sub_groups[{i}] should be LabelGroup, got {type(fetched_child)}"
        assert fetched_child.href in children_hrefs


@pytest.mark.integration
def test_nested_label_group_get_async(pce, nested_label_group_set, session_identifier):
    """
    Verifies that get_async() correctly deserializes nested sub-groups
    as LabelGroup objects. This is the exact scenario from APPS-1412.
    """
    parent, children, labels = nested_label_group_set

    # Fetch all label groups using get_async (the method that originally failed)
    label_groups = pce.label_groups.get_async(params={'name': session_identifier})

    # Find the parent label group in results
    fetched_parent = next((lg for lg in label_groups if lg.href == parent.href), None)
    assert fetched_parent is not None, "Parent label group not found in get_async results"

    assert fetched_parent.name == parent.name
    assert len(fetched_parent.sub_groups) == len(children)

    # Verify ALL nested children are correctly deserialized as LabelGroup
    children_hrefs = {child.href for child in children}
    for i, fetched_child in enumerate(fetched_parent.sub_groups):
        assert isinstance(fetched_child, LabelGroup), \
            f"sub_groups[{i}] should be LabelGroup, got {type(fetched_child)}"
        assert fetched_child.href in children_hrefs


@pytest.mark.integration
def test_label_group_labels_field(pce, nested_label_group_set):
    """
    Verifies that labels within a label group are correctly deserialized
    as Reference objects with all expected fields.
    """
    parent, children, test_labels = nested_label_group_set

    fetched = pce.label_groups.get_by_reference(parent.href)

    assert len(fetched.labels) == len(test_labels)

    test_label_hrefs = {label.href for label in test_labels}
    for label in fetched.labels:
        assert isinstance(label, Reference)
        assert label.href in test_label_hrefs


@pytest.mark.integration
def test_child_label_group_fields(pce, nested_label_group_set):
    """
    Verifies that child label groups have their own fields correctly populated.
    """
    parent, children, labels = nested_label_group_set

    fetched_parent = pce.label_groups.get_by_reference(parent.href)

    for fetched_child in fetched_parent.sub_groups:
        # Sub-groups should have at minimum href and name
        assert fetched_child.href is not None
        assert fetched_child.name is not None

        # Fetch the full child to verify all fields
        full_child = pce.label_groups.get_by_reference(fetched_child.href)

        assert full_child.href == fetched_child.href
        assert full_child.name == fetched_child.name
        assert full_child.key == 'app'
        assert full_child.description is not None
        assert 'Child label group' in full_child.description
        assert full_child.created_at is not None
        assert full_child.updated_at is not None
        assert isinstance(full_child.created_by, Reference)
        assert isinstance(full_child.updated_by, Reference)
