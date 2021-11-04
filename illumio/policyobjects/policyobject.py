from abc import ABC, abstractmethod


class PolicyObject(ABC):
    @abstractmethod
    def to_json(self) -> dict:
        pass
