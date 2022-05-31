# -*- coding: utf-8 -*-

"""This module is a stub for security principal objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass

from illumio.util import ModifiableObject, pce_api


@dataclass
@pce_api('security_principals')
class SecurityPrincipal(ModifiableObject):
    sid: str = None
