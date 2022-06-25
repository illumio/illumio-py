import pytest

from illumio.policyobjects import LabelSet
from illumio.rules import RuleSet

from helpers import random_string


@pytest.fixture
def rule_set(pce, session_identifier, app_label, env_label, loc_label):
    identifier = random_string()
    rule_set = pce.rule_sets.create(
        RuleSet(
            name='{}-RS-{}'.format(session_identifier, identifier),
            description='Created by illumio python library integration tests',
            enabled=True,
            scopes=[LabelSet(labels=[app_label, env_label, loc_label])],
            external_data_set=session_identifier,
            external_data_reference=identifier
        )
    )
    yield rule_set
    pce.rule_sets.delete(rule_set.href)

__all__ = ['rule_set']
