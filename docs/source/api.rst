.. _api:

.. module:: illumio

Developer Interface
===================

PCE Interface
-------------

Every PCE API endpoint is accessed through the
:class:`PolicyComputeEngine <PolicyComputeEngine>` object.

.. _pce:

.. autoclass:: PolicyComputeEngine
    :inherited-members:

.. autoclass:: illumio.pce::PolicyComputeEngine._PCEObjectAPI
    :inherited-members:
    :member-order: bysource

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

.. rubric:: Workloads

.. autoclass:: illumio.workloads.Workload

.. rubric:: VENs

.. autoclass:: illumio.workloads.VEN

.. rubric:: Pairing Profiles

.. autoclass:: illumio.workloads.PairingProfile

Security Policy
---------------

.. _rules:

.. rubric:: Rule Sets

.. autoclass:: illumio.rules.RuleSet

.. rubric:: Rules

.. autoclass:: illumio.rules.Rule
.. autofunction:: illumio.rules.Rule.build

.. rubric:: Enforcement Boundaries

.. autoclass:: illumio.rules.EnforcementBoundary
.. autofunction:: illumio.rules.EnforcementBoundary.build

Policy Objects
--------------

.. _policyobjects:

.. rubric:: IP Lists

.. autoclass:: illumio.policyobjects.IPList

.. rubric:: Labels

.. autoclass:: illumio.policyobjects.Label
.. autoclass:: illumio.policyobjects.LabelUsage
.. autoclass:: illumio.policyobjects.LabelGroup
.. autoclass:: illumio.policyobjects.LabelSet

.. rubric:: Services

.. autoclass:: illumio.policyobjects.Service

.. rubric:: Virtual Services

.. autoclass:: illumio.policyobjects.VirtualService

Infrastructure
--------------

.. _infrastructure:

.. rubric:: Container Clusters

.. autoclass:: illumio.infrastructure.ContainerCluster

Explorer
--------

.. _explorer:

.. rubric:: Traffic Analysis

.. autoclass:: illumio.explorer.TrafficQuery
.. autofunction:: illumio.explorer.TrafficQuery.build

.. autoclass:: illumio.explorer.TrafficFlow

Access Management
-----------------

.. _accessmanagement:

.. rubric:: Users

.. autoclass:: illumio.accessmanagement.User

Internal Utilities
------------------

.. _util:

.. autosummary::
    :toctree: generated
    :recursive:

    illumio.util
