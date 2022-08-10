.. _api:

.. currentmodule:: illumio

Developer Interface v\ |version|
================================

PCE Interface
-------------

PCE API endpoints are accessed through the ``PolicyComputeEngine`` object.

.. _pce:

.. autoclass:: PolicyComputeEngine
    :inherited-members:

.. autoclass:: illumio.pce::PolicyComputeEngine._PCEObjectAPI
    :inherited-members:
    :member-order: bysource

----------

PolicyComputeEngine API Attributes
##################################

The :class:`PolicyComputeEngine <PolicyComputeEngine>` class provides the following attributes:

|APIList|

Each represents a corresponding PCE API endpoint, implemented as a
:class:`_PCEObjectAPI <illumio.pce.PolicyComputeEngine._PCEObjectAPI>` instance.

Exceptions
----------

.. _exceptions:

The library uses two exception types to capture errors returned from the API or
encountered in other library functions.

.. autoexception:: IllumioException
.. autoexception:: IllumioApiException

Workloads and VENs
------------------

.. _workloads:

Workloads
#########

.. autoclass:: illumio.workloads.Workload

VENs
####

.. autoclass:: illumio.workloads.VEN

Pairing Profiles
################

.. autoclass:: illumio.workloads.PairingProfile

Security Policy
---------------

.. _rules:

Rule Sets
#########

.. autoclass:: illumio.rules.RuleSet

Rules
#####

.. autoclass:: illumio.rules.Rule
.. autofunction:: illumio.rules.Rule.build

Enforcement Boundaries
######################

.. autoclass:: illumio.rules.EnforcementBoundary
.. autofunction:: illumio.rules.EnforcementBoundary.build

Policy Objects
--------------

.. _policyobjects:

IP Lists
########

.. autoclass:: illumio.policyobjects.IPList

Labels
######

.. autoclass:: illumio.policyobjects.Label
.. autoclass:: illumio.policyobjects.LabelUsage
.. autoclass:: illumio.policyobjects.LabelGroup
.. autoclass:: illumio.policyobjects.LabelSet

Services
########

.. autoclass:: illumio.policyobjects.Service

Virtual Services
################

.. autoclass:: illumio.policyobjects.VirtualService

.. autoclass:: illumio.policyobjects.ServiceBinding

Infrastructure
--------------

.. _infrastructure:

Container Clusters
##################

.. autoclass:: illumio.infrastructure.ContainerCluster

.. autoclass:: illumio.infrastructure.ContainerWorkloadProfile

Explorer
--------

.. _explorer:

Traffic Analysis
################

.. autoclass:: illumio.explorer.TrafficQuery
.. autofunction:: illumio.explorer.TrafficQuery.build

.. autoclass:: illumio.explorer.TrafficFlow

Access Management
-----------------

.. _accessmanagement:

Users
#####

.. autoclass:: illumio.accessmanagement.User

Utilities
---------

Contains global constants, helper functions, and internal structures.

.. _util:

Constants
#########

.. autodata:: illumio.util.constants.ACTIVE

.. autodata:: illumio.util.constants.DRAFT

.. autodata:: illumio.util.constants.AMS

.. autodata:: illumio.util.constants.ANY_IP_LIST_NAME

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

Helper Functions
################

.. autofunction:: illumio.util.functions.convert_active_href_to_draft
.. autofunction:: illumio.util.functions.convert_draft_href_to_active
.. autofunction:: illumio.util.functions.convert_protocol
.. autofunction:: illumio.util.functions.deprecated
.. autofunction:: illumio.util.functions.ignore_empty_keys
.. autofunction:: illumio.util.functions.parse_url
.. autofunction:: illumio.util.functions.pce_api
