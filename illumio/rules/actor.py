import re
from dataclasses import dataclass

from illumio.exceptions import IllumioException
from illumio.util import JsonObject, Reference, HREF_REGEX

AMS = 'ams'


@dataclass
class Actor(JsonObject):
    actors: str = None
    label: Reference = None
    label_group: Reference = None
    workload: Reference = None
    virtual_service: Reference = None
    virtual_server: Reference = None
    ip_list: Reference = None

    @staticmethod
    def from_href(href):
        if href.lower() == AMS:  # special case for all objects
            return Actor(actors=AMS)
        actor = Actor()
        match = re.match(HREF_REGEX, href)
        if match:
            # HREF object types are plural, so we remove the s
            object_type = match.group('type')[:-1]
            setattr(actor, object_type, Reference(href=href))
        else:
            raise IllumioException('Invalid HREF in policy provision changeset: {}'.format(href))
        return actor

    def _decode_complex_types(self):
        self.label = Reference.from_json(self.label) if self.label else None
        self.label_group = Reference.from_json(self.label_group) if self.label_group else None
        self.workload = Reference.from_json(self.workload) if self.workload else None
        self.virtual_service = Reference.from_json(self.virtual_service) if self.virtual_service else None
        self.virtual_server = Reference.from_json(self.virtual_server) if self.virtual_server else None
        self.ip_list = Reference.from_json(self.ip_list) if self.ip_list else None
