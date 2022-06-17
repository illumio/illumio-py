# -*- coding: utf-8 -*-

"""This module is a stub for container cluster objects.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass

from illumio.util import MutableObject, pce_api


@dataclass
@pce_api('container_clusters')
class ContainerCluster(MutableObject):
    pass
