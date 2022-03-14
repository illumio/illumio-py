# -*- coding: utf-8 -*-

"""This module is a stub for enforcement boundary objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass

from .rule import BaseRule


@dataclass
class EnforcementBoundary(BaseRule):
    pass
