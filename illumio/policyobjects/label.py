import json
from dataclasses import dataclass
from typing import List

from illumio import JsonObject, ModifiableObject


@dataclass
class Label(ModifiableObject):
    key: str = None
    value: str = None
    deleted: bool = None


@dataclass
class LabelGroup(Label):
    labels: List[Label] = None
    sub_groups: List[dict] = None
    usage: dict = None

    def _decode_complex_types(self) -> None:
        super()._decode_complex_types()
        self.labels = [Label.from_json(o) for o in self.labels]


@dataclass
class LabelSet(JsonObject):
    labels: List[Label] = None

    def to_json(self):
        return [{'label_group' if type(label) is LabelGroup else 'label': label.to_json()} for label in self.labels]

    @classmethod
    def from_json(cls, data) -> 'LabelSet':
        data = json.loads(data) if type(data) is str else data
        labels = []
        for label_entry in data:
            key = 'label'
            label_type = Label
            if key not in label_entry:
                key = 'label_group'
                label_type = LabelGroup
            labels.append(label_type.from_json(label_entry[key]))
        return LabelSet(labels=labels)
