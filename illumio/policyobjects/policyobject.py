from dataclasses import dataclass

from .jsonobject import JsonObject


@dataclass
class Reference:
    href: str


@dataclass
class PolicyObject(JsonObject):
    href: str = None
    name: str = None
    description: str = None
    created_at: str = None
    updated_at: str = None
    deleted_at: str = None
    update_type: str = None
    created_by: Reference = None
    updated_by: Reference = None
    deleted_by: Reference = None

    def _decode_complex_types(self) -> None:
        self.created_by = Reference(**self.created_by) if self.created_by else None
        self.updated_by = Reference(**self.updated_by) if self.updated_by else None
        self.deleted_by = Reference(**self.deleted_by) if self.deleted_by else None
