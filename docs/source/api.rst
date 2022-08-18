.. _api:

.. currentmodule:: illumio

Developer Interface v\ |version|
================================

.. _pce:

PCE Interface
-------------

PolicyComputeEngine
###################

The ``PolicyComputeEngine`` object provides the core interface for interacting
with PCE API endpoints.

.. autoclass:: PolicyComputeEngine
    :inherited-members:

PCE Object API
##############

This internal class is used to represent API objects within the PCE, and provides
a common CRUD interface for them.

.. autoclass:: illumio.pce::PolicyComputeEngine._PCEObjectAPI
    :inherited-members:

.. _apiattributes:

PolicyComputeEngine API Attributes
##################################

The :class:`PolicyComputeEngine <PolicyComputeEngine>` class provides the following attributes:

|APIList|

Each represents a corresponding PCE API endpoint, implemented as a
:class:`_PCEObjectAPI <illumio.pce.PolicyComputeEngine._PCEObjectAPI>` instance.

.. _exceptions:

Exceptions
----------

The library uses two exception types to capture errors returned from the API or
encountered in other library functions.

.. autoexception:: IllumioException
.. autoexception:: IllumioApiException
.. autoexception:: IllumioIntegerValidationException

.. _events:

Events
------

.. autoclass:: Event

.. _workloads:

Workloads and VENs
------------------

Workloads
#########

.. autoclass:: illumio.workloads.Workload

VENs
####

.. autoclass:: illumio.workloads.VEN

Pairing Profiles
################

.. autoclass:: illumio.workloads.PairingProfile

.. _securitypolicy:

Security Policy
---------------

Rule Sets
#########

.. autoclass:: illumio.rules.RuleSet

Rules
#####

.. autoclass:: illumio.rules.Rule
    :members: build

Enforcement Boundaries
######################

.. autoclass:: illumio.rules.EnforcementBoundary
    :members: build

.. _policyobjects:

Policy Objects
--------------

IP Lists
########

.. autoclass:: illumio.policyobjects.IPList

Labels
######

.. autoclass:: illumio.policyobjects.Label
.. autoclass:: illumio.policyobjects.LabelGroup
.. autoclass:: illumio.policyobjects.LabelSet

Services
########

.. autoclass:: illumio.policyobjects.Service

Virtual Services
################

.. autoclass:: illumio.policyobjects.VirtualService

.. autoclass:: illumio.policyobjects.ServiceBinding

.. _infrastructure:

Infrastructure
--------------

Container Clusters
##################

.. autoclass:: illumio.infrastructure.ContainerCluster

.. autoclass:: illumio.infrastructure.ContainerWorkloadProfile

.. _explorer:

Explorer
--------

Traffic Analysis
################

.. autoclass:: illumio.explorer.TrafficQuery
    :members: build

.. autoclass:: illumio.explorer.TrafficFlow

.. _accessmanagement:

Access Management
-----------------

Users
#####

.. autoclass:: illumio.accessmanagement.User

.. _util:

Utilities
---------

Contains global constants, helper functions, and internal structures.

Constants
#########

.. autodata:: illumio.util.constants.ACTIVE
.. autodata:: illumio.util.constants.DRAFT
.. autodata:: illumio.util.constants.AMS
.. autodata:: illumio.util.constants.RESOLVE_AS_WORKLOADS
.. autodata:: illumio.util.constants.RESOLVE_AS_VIRTUAL_SERVICES
.. autodata:: illumio.util.constants.ANY_IP_LIST_NAME
.. autodata:: illumio.util.constants.ALL_SERVICES_NAME
.. autodata:: illumio.util.constants.PORT_MAX
.. autodata:: illumio.util.constants.ICMP_CODE_MAX
.. autodata:: illumio.util.constants.ICMP_TYPE_MAX
.. autodata:: illumio.util.constants.BULK_CHANGE_LIMIT

.. autoenum:: illumio.util.constants.EnforcementMode
    :members:

.. autoenum:: illumio.util.constants.LinkState
    :members:

.. autoenum:: illumio.util.constants.VisibilityLevel
    :members:

.. autoenum:: illumio.util.constants.Transmission
    :members:

.. autoenum:: illumio.util.constants.FlowDirection
    :members:

.. autoenum:: illumio.util.constants.TrafficState
    :members:

.. autoenum:: illumio.util.constants.ApplyTo
    :members:

.. autoenum:: illumio.util.constants.VENType
    :members:

.. autoenum:: illumio.util.constants.ChangeType
    :members:

.. autoenum:: illumio.util.constants.EventSeverity
    :members:

.. autoenum:: illumio.util.constants.EventStatus
    :members:

Helper Functions
################

.. autofunction:: illumio.util.functions.convert_active_href_to_draft
.. autofunction:: illumio.util.functions.convert_draft_href_to_active
.. autofunction:: illumio.util.functions.convert_protocol
.. autofunction:: illumio.util.functions.deprecated
.. autofunction:: illumio.util.functions.ignore_empty_keys
.. autofunction:: illumio.util.functions.parse_url
.. autofunction:: illumio.util.functions.pce_api

.. autofunction:: illumio.util.jsonutils.href_from

Base Classes
############

.. autoclass:: illumio.util.jsonutils.JsonObject
.. autoclass:: illumio.util.jsonutils.IllumioObject
.. autoclass:: illumio.util.jsonutils.Reference
