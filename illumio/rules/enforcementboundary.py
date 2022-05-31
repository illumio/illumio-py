# -*- coding: utf-8 -*-

"""This module is a stub for enforcement boundary objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass

from illumio.util import pce_api

from .rule import BaseRule


@dataclass
@pce_api('enforcement_boundaries', is_sec_policy=True)
class EnforcementBoundary(BaseRule):
    pass
