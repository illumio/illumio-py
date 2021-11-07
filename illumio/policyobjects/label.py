from dataclasses import dataclass, field
from typing import List

from .policyobject import PolicyObject

from illumio import IllumioException


@dataclass
class Label(PolicyObject):
    key: str = None
    value: str = None
    deleted: bool = None
    external_data_set: str = None
    external_data_reference: str = None

    def __post_init__(self):
        if not self.key or not self.value:
            raise IllumioException("Invalid Label - both key and value are required")


@dataclass
class LabelGroup(Label):
    labels: List[Label] = None
    sub_groups: List[dict] = None
    usage: dict = None

    def __post_init__(self):
        if not self.name or not self.key:
            raise IllumioException("Invalid LabelGroup - both key and name are required")

    def _decode_complex_types(self) -> None:
        super()._decode_complex_types()
        self.labels = [Label.from_json(o) for o in self.labels]
