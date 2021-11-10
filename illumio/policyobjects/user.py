from dataclasses import dataclass

from .policyobject import PolicyObject


@dataclass
class User(PolicyObject):
    username: str = None
    last_login_on: str = None
    last_login_ip_address: str = None
    login_count: int = None
    full_name: str = None
    time_zone: str = None
    locked: bool = None
    effective_groups: list = None
    local_profile: dict = None
    type: str = None
    presence_status: str = None


@dataclass
class UserObject(PolicyObject):
    created_by: User = None
    updated_by: User = None
    deleted_by: User = None

    def _decode_complex_types(self) -> None:
        self.created_by = User(**self.created_by) if self.created_by else None
        self.updated_by = User(**self.updated_by) if self.updated_by else None
        self.deleted_by = User(**self.deleted_by) if self.deleted_by else None
