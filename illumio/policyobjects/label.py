from dataclasses import dataclass
from typing import List

from .user import UserObject


@dataclass
class Label(UserObject):
    key: str = None
    value: str = None
    deleted: bool = None
    external_data_set: str = None
    external_data_reference: str = None


@dataclass
class LabelGroup(Label):
    labels: List[Label] = None
    sub_groups: List[dict] = None
    usage: dict = None

    def _decode_complex_types(self) -> None:
        super()._decode_complex_types()
        self.labels = [Label.from_json(o) for o in self.labels]
