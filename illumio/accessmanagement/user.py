from dataclasses import dataclass

from illumio import IllumioObject


@dataclass
class User(IllumioObject):
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
