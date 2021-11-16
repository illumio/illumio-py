from dataclasses import dataclass

from illumio.util.jsonutils import JsonObject
from illumio.policyobjects import (
    IPList,
    Label,
    LabelGroup,
    VirtualServer,
    VirtualService
)
from illumio.workloads import Workload


@dataclass
class Actor(JsonObject):
    actors: str = None
    label: Label = None
    label_group: LabelGroup = None
    workload: Workload = None
    virtual_service: VirtualService = None
    virtual_server: VirtualServer = None
    ip_list: IPList = None

    def _decode_complex_types(self):
        self.label = Label.from_json(self.label) if self.label else None
        self.label_group = LabelGroup.from_json(self.label_group) if self.label_group else None
        self.workload = Workload.from_json(self.workload) if self.workload else None
        self.virtual_service = VirtualService.from_json(self.virtual_service) if self.virtual_service else None
        self.virtual_server = VirtualServer.from_json(self.virtual_server) if self.virtual_server else None
        self.ip_list = IPList.from_json(self.ip_list) if self.ip_list else None
