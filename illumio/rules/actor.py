from dataclasses import dataclass

from illumio.util import JsonObject, Reference


@dataclass
class Actor(JsonObject):
    actors: str = None
    label: Reference = None
    label_group: Reference = None
    workload: Reference = None
    virtual_service: Reference = None
    virtual_server: Reference = None
    ip_list: Reference = None

    def _decode_complex_types(self):
        self.label = Reference.from_json(self.label) if self.label else None
        self.label_group = Reference.from_json(self.label_group) if self.label_group else None
        self.workload = Reference.from_json(self.workload) if self.workload else None
        self.virtual_service = Reference.from_json(self.virtual_service) if self.virtual_service else None
        self.virtual_server = Reference.from_json(self.virtual_server) if self.virtual_server else None
        self.ip_list = Reference.from_json(self.ip_list) if self.ip_list else None
