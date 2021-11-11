from dataclasses import dataclass

from illumio import JsonObject


@dataclass
class PolicyObject(JsonObject):
    href: str = None
    name: str = None
    description: str = None
    created_at: str = None
    updated_at: str = None
    deleted_at: str = None
    update_type: str = None
    delete_type: str = None
