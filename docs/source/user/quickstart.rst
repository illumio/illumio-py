.. _quickstart:

.. currentmodule:: illumio

Quickstart Guide
================

This document provides a basic introduction to the core features of the
**illumio** library, from connecting to the Illumio Policy Compute Engine
to creating and provisioning policy.

Make sure you have the library :ref:`installed <install>`, then read on for
some simple examples.

.. note::

    This guide assumes a base level of familiarity with the PCE APIs. Refer to the
    `Illumio PCE REST API Developer Guide <https://docs.illumio.com/core/21.5/Content/LandingPages/Guides/rest-api.htm>`_
    or the `PCE API reference <https://docs.illumio.com/core/21.5/API-Reference/index.html>`_
    for your PCE version for a more complete introduction to API usage and schema.

.. _pceconnect:

Connect to the PCE
------------------

The first step for any application will be to connect to the Policy Compute Engine.
The **illumio** library makes this simple with the :class:`PolicyComputeEngine <PolicyComputeEngine>` class::

    >>> from illumio import PolicyComputeEngine
    >>> pce = PolicyComputeEngine('my.pce.com', port=443, org_id=1)

.. note::
    The first ``PolicyComputeEngine`` parameter can be passed as a URL - useful
    if your PCE instance does not have TLS certificates configured - or as an
    FQDN as shown above. When passing just the domain name, the scheme will
    default to ``https://``.

In order to access the PCE API endpoints, we now need to provide credentials to
authorize our ``pce`` instance::

    >>> pce.set_credentials('api_key', 'api_secret')

.. note::
    Both username/password and API key/secret values can be passed to :meth:`set_credentials <PolicyComputeEngine.set_credentials>`.

Now that we've set up our connection details, we can confirm that our connection is working::

    >>> print(pce.check_connection())
    True

Great! With only a few lines of code, we now have a working, persistent connection
to our PCE that we can use to interact with the PCE APIs.

.. _apiendpoints:

API Endpoints
-------------

PCE API CRUD endpoints are registered as attributes in :class:`PolicyComputeEngine <PolicyComputeEngine>`,
represented by instances of the internal :class:`_PCEObjectAPI <illumio.pce.PolicyComputeEngine._PCEObjectAPI>` class.

Each one implements a standard interface to manage objects in the PCE.
The full list can be found in the :ref:`API documentation <apiattributes>`.

.. code:: python

    >>> from illumio import IPList, IPRange, FQDN
    >>> ip_lists = pce.ip_lists.get(params={'max_results': 5})
    >>> ip_lists
    [
        IPList(href='/orgs/1/sec_policy/draft/ip_lists/1', ...),
        ...
    ]
    >>> new_ip_list = pce.ip_lists.create(
    ...     IPList(
    ...         name='IPL-Private',
    ...         ip_ranges=[
    ...             IPRange(from_ip='127.0.0.1'),
    ...             IPRange(from_ip='172.16.0.0', to_ip='172.31.255.255'),
    ...             IPRange(from_ip='192.168.0.0/16')
    ...         ]
    ...     )
    ... )
    >>> new_ip_list
    IPList(href='/orgs/1/sec_policy/draft/ip_lists/12', ...)
    >>> pce.ip_lists.update(new_ip_list, {'fqdns': [FQDN(fqdn='localhost')]})
    >>> updated_ip_list = pce.ip_lists.get_by_reference(new_ip_list.href)
    >>> updated_ip_list
    IPList(href='/orgs/1/sec_policy/draft/ip_lists/12', fqdns=[FQDN(fqdn='localhost')], ...)
    >>> pce.ip_lists.delete(new_ip_list)

In addition to the CRUD operations shown above, the ``_PCEObjectAPI`` class also
provides functions for asynchronous and batch operations - see the
:ref:`Advanced Usage guide <advanced>` for details.

.. note:: HTTP requests
    The **illumio** library uses **requests** under the hood to communicate with the PCE.
    The various request functions accept the same keyword arguments as their **requests**
    counterparts, allowing query parameters, headers, body data, cookies, certificates,
    and other HTTP features to be specified.
    See the `requests documentation <https://requests.readthedocs.io/en/latest/>`_
    for the full specification.

References
----------

PCE objects use an HREF as a unique identifier. The HREF is typically made up of the
organization reference and object path::

    /orgs/1/labels/1

This HREF is used to **GET** individual objects and in request/response bodies to
reference dependent or nested objects.

Where references are required, the **illumio** library generally accepts HREF string
literals, dictionaries containing an ``href`` key, or a :class:`Reference <illumio.util.jsonutils.Reference>`
object. The ``Reference`` class is a base type extended by most PCE objects.


.. rubric:: HREF string

.. code:: python

    >>> label = pce.labels.get_by_reference('/orgs/1/labels/1')
    >>> label
    Label(href='/orgs/1/labels/1', ...)

.. rubric:: Dictionary

.. code:: python

    >>> label = pce.labels.get_by_reference({'href': '/orgs/1/labels/1'})
    >>> label
    Label(href='/orgs/1/labels/1', ...)

.. rubric:: ``Reference`` object

.. code:: python

    >>> import illumio
    >>> label_ref = illumio.Reference(href='/orgs/1/labels/1')
    >>> label = pce.labels.get_by_reference(label_ref)
    >>> label
    Label(href='/orgs/1/labels/1', ...)

API Responses
-------------

The convenience functions in :class:`_PCEObjectAPI <illumio.pce.PolicyComputeEngine._PCEObjectAPI>`
wrap the JSON responses from the PCE and return python objects of the expected type. While these
should be sufficient for most use-cases, the underlying :meth:`get <PolicyComputeEngine.get>`,
:meth:`post <PolicyComputeEngine.post>`, :meth:`put <PolicyComputeEngine.put>`,
:meth:`delete <PolicyComputeEngine.delete>`, and :meth:`get_collection <PolicyComputeEngine.get_collection>`
functions are exposed for unimplemented or custom PCE requests::

    >>> pce.set_credentials('first.last@company.com', 'keepmesecret')
    >>> resp = pce.post('/users/1/api_keys', json={'name': 'ILLUMIO_PY'}, include_org=False)
    >>> api_key_response = resp.json()
    >>> api_key_response
    {'key_id': '11ce8a65cde969f8f', 'auth_username': 'api_11ce8a65cde969f8f', 'secret': '...'}
    >>> pce.set_credentials(api_key_response['auth_username'], api_key_response['secret'])

These functions return the ``requests.Response`` object directly. For supported
objects, the JSON response can be converted to its Python equivalent using
:meth:`from_json <illumio.util.jsonutils.JsonObject.from_json>`::

    >>> from illumio import Service
    >>> resp = pce.get('/sec_policy/active/services/1')
    >>> service = Service.from_json(resp.json())
    >>> service
    Service(href='/orgs/1/sec_policy/active/services/1', name='All Services', ...)

Working with Policy Objects
---------------------------

Segmenting your network using the PCE is achieved through `security policy <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/overview/illumio-policy-model.htm>`_
defined using `policy objects <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/_ch-security-policy-objects.htm>`_.

Security Rules, scoped within Rule Sets, provide a flexible way to define
allow-list policies for your workloads. IP Lists and Services provide abstraction
and grouping for ingress and egress. Labels and Label Groups categorize workloads,
defining policy scope in an extensible and human-readable way.

.. rubric:: Representing Application Boundaries with Labels

The Illumio Policy Compute Engine provides four label dimensions: Role,
Application, Environment, and Location. Using these, we can create logical
boundaries for workloads within which to define policy rules.

Let's take a look at an example.

.. code:: python

    >>> from illumio import Label
    >>> role_label = pce.labels.create(Label(key='role', value='R-NTP'))
    >>> app_label = pce.labels.create(Label(key='app', value='A-CoreServices'))
    >>> env_label = pce.labels.create(Label(key='env', value='E-Prod'))
    >>> loc_label = pce.labels.create(Label(key='loc', value='L-AWS'))
    >>> ntp_server = pce.workloads.create(
    ...     Workload(
    ...         name='Internal NTP',
    ...         hostname='ntp0.lab.company.com',
    ...         public_ip='10.8.0.17',
    ...         labels= [role_label, app_label, env_label, loc_label]
    ...     )
    ... )
    >>> ntp_server
    Workload(
        href='/orgs/1/workloads/644418c6-fdf7-4008-87d7-d023019a6f0d',
        name='Internal NTP',
        ...
    )

Based on these labels, it's clear that this `unmanaged workload <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/workloads/workload-setup-using-pce-web-console.htm#UnmanagedWorkloads>`_
represents an NTP server in our Production Core Services application running in AWS.

Check out the :ref:`nano-segmentation use-case <nanosegmentation>` for a
more detailed example of how labels can be used to simplify policy definition
for complex applications, or further explore how labels can be applied to
workloads in the :ref:`workload labelling use-case <workloadlabelling>`.

.. _provisioning:

.. rubric:: Policy Provisioning

Objects in the PCE that directly affect your network's security policy -- such
as Rules, IP Lists, Enforcement Boundaries, and Virtual Services -- are initially
created in a **draft** state. Changes to these objects will show up in
`Illumination's Draft view <https://docs.illumio.com/core/21.5/Content/Guides/introduction/visualization-overview.htm#DraftvsReportedintheMaps>`_
so that their impact can be reviewed before being applied.

The GET functions in :class:`_PCEObjectAPI <illumio.pce.PolicyComputeEngine._PCEObjectAPI>`
provide a ``policy_version`` parameter to specify whether **draft** or **active**
state objects should be returned from the PCE.

.. note::
    By default, these functions return **draft** objects as all PCE objects have
    a draft representation that may or may not be the same as its active version.
    Any operations that modify the object must be performed on the draft version,
    then provisioned.

To apply policy in **draft** state, we have to `provision <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/create-security-policy/provisioning.htm>`_
the change to create or update the **active** version of impacted policy objects.

.. code:: python

    >>> from illumio import LabelGroup
    >>> env_labels = pce.labels.get(params={'key': 'env', 'max_results': 10})
    >>> preprod_envs = ['Test', 'Staging', 'Development']
    >>> preprod_labels = [label for label in env_labels if label.value in preprod_envs]
    >>> label_group = pce.label_groups.create(
    ...     LabelGroup(
    ...         name='LG-E-PreProd',
    ...         key='env',
    ...         labels=preprod_labels
    ...     )
    ... )
    >>> label_group
    LabelGroup(
        href='/orgs/1/sec_policy/draft/label_groups/c6a57d39-ccfa-4454-ad2e-7255b5a777ba',
        name='LG-E-PreProd',
        ...
    )
    >>> policy_version = pce.provision_policy_changes(
    ...     change_description="Create pre-production environments label group",
    ...     hrefs=[label_group.href]
    ... )
    >>> policy_version
    PolicyVersion(
        href='/orgs/1/sec_policy/38',
        commit_message='Create pre-production environments label group',
        ...
    )

.. note::
    Objects in **draft** state that haven't been provisioned do not have **active**
    representations, and DELETE requests on them will remove the object without
    needing a provision request.
