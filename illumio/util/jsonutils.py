import json
from typing import Any

_default = json.JSONEncoder()  # fall back to the default encoder for non-Illumio API objects


class IllumioEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return getattr(o.__class__, "to_json", _default.default)(o)
