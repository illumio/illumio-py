# -*- coding: utf-8 -*-

"""This module provides classes related to labels and label groups.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
import json
from dataclasses import dataclass
from typing import List

from illumio.util import JsonObject, ModifiableObject


@dataclass
class LabelUsage(JsonObject):
    label_group: bool = None
    ruleset: bool = None
    rule: bool = None
    static_policy_scopes: bool = None
    containers_inherit_host_policy_scopes: bool = None
    blocked_connection_reject_scope: bool = None
    enforcement_boundary: bool = None


@dataclass
class Label(ModifiableObject):
    key: str = None
    value: str = None
    deleted: bool = None
    usage: LabelUsage = None


@dataclass
class LabelGroup(Label):
    labels: List[Label] = None
    sub_groups: List['LabelGroup'] = None


@dataclass
class LabelSet(JsonObject):
    labels: List[Label] = None

    def _encode(self):
        json_array = []
        for label in self.labels:
            key = 'label_group' if '/label_groups/' in label.href else 'label'
            json_array.append({key: label.to_json()})
        return json_array

    @classmethod
    def from_json(cls, data) -> 'LabelSet':
        data = json.loads(data) if type(data) is str else data
        labels = []
        for label_entry in data:
            key = 'label' if 'label' in label_entry else 'label_group'
            labels.append(Label.from_json(label_entry[key]))
        return LabelSet(labels=labels)
