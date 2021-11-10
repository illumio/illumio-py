from dataclasses import dataclass

from .user import UserObject


@dataclass
class ContainerCluster(UserObject):
    score: int = None
