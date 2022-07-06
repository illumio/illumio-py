from illumio.util import DRAFT


def test_get_by_reference(pce, rule_set):
    rs = pce.rule_sets.get_by_reference(rule_set.href)
    assert rs.href == rule_set.href


def test_get_by_partial_name(pce, session_identifier, rule_set):
    rule_sets = pce.rule_sets.get(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(rule_sets) == 1


def test_get_async(pce, session_identifier, rule_set):
    rule_sets = pce.rule_sets.get_async(params={'name': session_identifier}, policy_version=DRAFT)
    assert len(rule_sets) == 1


def test_update_rule_set(pce, rule_set):
    pce.rule_sets.update(
        rule_set.href,
        {
            'description': 'Integration test update. Disable rule set.',
            'enabled': False
        }
    )
    rs = pce.rule_sets.get_by_reference(rule_set.href)
    assert rs.enabled == False
