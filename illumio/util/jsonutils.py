# -*- coding: utf-8 -*-

"""This module provides the core of the class model used in the client.

The base JsonObject class handles basic encoding and decoding to translate
responses from the PCE REST API into python objects. The implementation
leverages dataclasses to simplify the logic for these operations.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
import copy
import json
from abc import ABC
from dataclasses import dataclass, fields
from inspect import signature, isclass
from typing import List, Any

from illumio.exceptions import IllumioException

from .constants import IllumioEnumMeta
from .functions import ignore_empty_keys, isunion, islist

_default = json.JSONEncoder()  # fall back to the default encoder for non-Illumio API objects


class IllumioEncoder(json.JSONEncoder):
    """Convenience class for encoding JsonObjects.

    >>> json.dumps(flow, cls=IllumioEncoder, indent=4)
    """
    def default(self, o: Any) -> Any:
        return getattr(o.__class__, "to_json", _default.default)(o)


@dataclass
class JsonObject(ABC):

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            self._flatten_ref(field, value)
            self._resolve_enum(field, value)
        self._validate()

    def _resolve_enum(self, field, value):
        """Replaces IllumioEnumMeta subtypes with their internal value.

        This allows clients to pass enums directly as attribute values.

        For example:

        >>> Workload(..., enforcement_mode=EnforcementMode.SELECTIVE)

        will be converted to

        >>> Workload(..., enforcement_mode='selective')
        """
        if value is None:
            return
        if isinstance(type(value), IllumioEnumMeta):
            setattr(self, field.name, value.value)

    def _flatten_ref(self, field, value):
        """Replaces Reference subclasses with a simplified Reference object.

        This allows clients to pass a Reference subclass instance without
        breaking the encoded object schema for API calls.
        """
        if value is None:
            return
        if field.type is Reference:
            if isinstance(value, Reference):
                setattr(self, field.name, Reference(value.href))
        elif islist(field.type):
            if field.type.__args__[0] is Reference:
                ref_list = []
                for ref in value:
                    if isinstance(ref, Reference):
                        ref_list.append(Reference(href=ref.href))
                    else:
                        ref_list.append(ref)
                setattr(self, field.name, ref_list)
        elif isunion(field.type):
            if Reference in field.type.__args__:
                if isinstance(value, Reference):
                    setattr(self, field.name, Reference(value.href))

    def _validate(self):
        """Validates fields by comparing their values to their registered dataclass types."""
        for field in fields(self):
            value = getattr(self, field.name)
            if not self._validate_field(field.type, value):
                raise AttributeError("Invalid value for {}: {}. Must be of type {}".format(field.name, value, field.type))

    def _validate_field(self, expected_type, value) -> bool:
        if value is None:
            return True
        elif expected_type is object:
            return True
        elif type(value) == expected_type:
            return True
        elif isunion(expected_type):
            return any(self._validate_field(type_, value) for type_ in expected_type.__args__)
        elif isclass(expected_type) and issubclass(expected_type, JsonObject):
            # if the object is already decoded, determine whether it's
            # a subtype of what the field expects
            if isinstance(value, JsonObject):
                return isinstance(value, expected_type)
            # XXX: otherwise, expand objects to run their own validation.
            #   this is *slow*, but needed to validate deeply nested types
            expected_type.from_json(value)
            return True
        elif islist(expected_type) and isinstance(value, list):
            if not value:
                return True  # empty lists are always valid
            expected_type = expected_type.__args__[0]
            return all(self._validate_field(expected_type, o) for o in value)
        return False

    def to_json(self) -> Any:
        return deep_encode(self)

    @classmethod
    def from_json(cls, data: Any) -> 'JsonObject':
        """
        Given a JSON object or dictionary, decodes the data as an object
        of the calling JsonObject subtype. Accepts arbitrary key/value pairs
        as a form of forwards-compatibility.

        Classes can optionally extend decoding with the _decode_complex_types
        function for complex-type members.

        Based in part on https://stackoverflow.com/a/55101438
        """
        data = json.loads(data) if type(data) is str else data
        cls_fields = {field for field in signature(cls).parameters}

        defined_params, undefined_params = {}, {}
        for k, v in data.items():
            if k in cls_fields:
                defined_params[k] = v
            else:
                undefined_params[k] = v

        o = cls(**defined_params)

        for k, v in undefined_params.items():
            setattr(o, k, v)

        o._decode_complex_types()
        return o

    def _decode_complex_types(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            decoded_value = self._decode_field(field.type, value)
            setattr(self, field.name, decoded_value)

    def _decode_field(self, type_, value) -> Any:
        if value is None:
            return None
        if isinstance(value, JsonObject):
            # if the value has already been decoded, return it
            return value
        elif isclass(type_) and issubclass(type_, JsonObject):
            return type_.from_json(value)
        elif isinstance(value, list):
            # if the value is a list, expect the field type to be List[T]
            type_ = type_.__args__[0]
            return list(self._decode_field(type_, o) for o in value)
        return value


def deep_encode(o: Any) -> Any:
    """
    Recursively encode members of the given object and return a JSON-compatible
    copy. Children of the JsonObject superclass can optionally implement an
    _encode method to provide a customized encoding response, otherwise the
    default ignore_empty_keys function is called to remove null value pairs.

    Functionally similar to the dataclasses asdict method, but with the necessary
    adjustment of calling an optional custom encoding function for types that
    don't strictly mirror their dataclass field pairs when encoded.
    """
    if isinstance(o, JsonObject):
        result = []
        if hasattr(type(o), '_encode'):
            return o._encode()
        for f in fields(o):
            value = deep_encode(getattr(o, f.name))
            result.append((f.name, value))
        return ignore_empty_keys(result)
    elif isinstance(o, (list, tuple)):
        return type(o)(deep_encode(o) for o in o)
    elif isinstance(o, dict):
        return type(o)((deep_encode(k), deep_encode(v)) for k, v in o.items())
    else:
        return copy.deepcopy(o)


@dataclass
class Reference(JsonObject):
    href: str = None


def href_from(reference: Any):
    """Attempts to parse HREF value from a provided source."""
    if isinstance(reference, Reference):
        return reference.href
    elif type(reference) is dict:
        if 'href' in reference:
            return reference['href']
    elif type(reference) is str:
        return reference
    raise IllumioException('Failed to extract HREF from value: {}'.format(reference))


@dataclass
class IllumioObject(Reference):
    name: str = None
    description: str = None
    external_data_set: str = None
    external_data_reference: str = None


@dataclass
class MutableObject(IllumioObject):
    created_at: str = None
    updated_at: str = None
    deleted_at: str = None
    update_type: str = None
    delete_type: str = None
    created_by: Reference = None
    updated_by: Reference = None
    deleted_by: Reference = None
    caps: List[str] = None


@dataclass
class ImmutableObject(IllumioObject):
    created_at: str = None
    created_by: Reference = None
