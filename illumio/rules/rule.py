# -*- coding: utf-8 -*-

"""This module provides classes related to policy rules.

Copyright:
    (c) 2022 Illumio

License:
    Apache2, see LICENSE for more details.
"""
from dataclasses import dataclass
from typing import List, Union

from illumio.util import JsonObject, Reference, ModifiableObject
from illumio.policyobjects import Service, ServicePort

from .actor import Actor


@dataclass
class BaseRule(ModifiableObject):
    ingress_services: List[Union[Service, ServicePort]] = None
    providers: List[Actor] = None
    consumers: List[Actor] = None

    @classmethod
    def build(cls, providers: List[str], consumers: List[str],
            ingress_services: List[Union[JsonObject, dict, str]], **kwargs) -> 'BaseRule':
        services = []
        for service in ingress_services:
            if type(service) is JsonObject:
                services.append(service)
            elif type(service) is str:
                services.append(Service(href=service))
            else:
                service_type = Service if 'href' in service else ServicePort
                services.append(service_type.from_json(service))
        return cls(
            providers=[Actor.from_href(provider) for provider in providers],
            consumers=[Actor.from_href(consumer) for consumer in consumers],
            ingress_services=services,
            **kwargs
        )

    def _decode_complex_types(self):
        decoded_ingress_services = []
        for service in self.ingress_services:
            service_type = Service if 'href' in service else ServicePort
            decoded_ingress_services.append(service_type.from_json(service))
        self.ingress_services = decoded_ingress_services
        super()._decode_complex_types()


@dataclass
class LabelResolutionBlock(JsonObject):
    providers: List[str] = None
    consumers: List[str] = None


@dataclass
class Rule(BaseRule):
    enabled: bool = None
    resolve_labels_as: LabelResolutionBlock = None
    sec_connect: bool = None
    stateless: bool = None
    machine_auth: bool = None
    consuming_security_principals: List[Reference] = None
    unscoped_consumers: bool = None
    network_type: str = None

    @classmethod
    def build(cls, providers: List[str], consumers: List[str], ingress_services: List[dict],
            resolve_providers_as: List[str], resolve_consumers_as: List[str], **kwargs) -> 'Rule':
        resolve_labels_as = LabelResolutionBlock(providers=resolve_providers_as, consumers=resolve_consumers_as)
        return super().build(providers, consumers, ingress_services, resolve_labels_as=resolve_labels_as, **kwargs)
