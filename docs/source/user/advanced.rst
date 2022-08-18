.. _advanced:

.. currentmodule:: illumio

Advanced Usage
==============

This document explains some of the **illumio** library and the Policy Compute
Engine's more complex features.

Proxy Settings
--------------

If you need to use a proxy to communicate with the PCE, HTTP/S proxies can be
configured using the :meth:`set_proxies <PolicyComputeEngine.set_proxies>`
function::

    >>> pce.set_proxies(
    ...     http_proxy='http://my.proxyserver.com:8080',
    ...     https_proxy='http://my.proxyserver.com:8080'
    ... )

If not set in the session, the ``requests`` library will pull proxy settings
from environment variables, see the ``requests`` `proxy documentation <https://requests.readthedocs.io/en/latest/user/advanced/#proxies>`_
for details.

.. note::
    Proxy values set with ``set_proxies`` will apply to the session, and will
    be overwritten by proxy values set in the executing shell environment. If
    you need to override environment proxy settings, you can specify the
    ``proxies`` parameter directly as a keyword argument::

        >>> pce.ip_lists.get(proxies={'http': 'http://proxy.server:8080', 'https': 'http://proxy.server:8080'})

TLS Certificates
----------------

If you're using the **illumio** library with an on-prem PCE, you may be using
self-signed or internal ceriticate chains for your instance.

Requests through the :class:`PolicyComputeEngine <PolicyComputeEngine>` can
leverage the ``requests`` library ``verify`` and ``cert`` parameters to specify
CA certificates and cert/key pairs respectively.

See `the requests documentation <https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification>`_
for details.

Disable TLS verification::

    >>> pce.labels.get(verify=False)

Verify using custom CA bundle::

    >>> pce.labels.get(verify='/path/to/ca/bundle')

Verify using a local client-side cert pair::

    >>> pce.labels.get(verify=True, cert='/path/to/keypair.pem')
    >>> pce.labels.get(verify=True, cert=('/path/to/client.crt', '/path/to/client.key'))

Asynchronous Collection Requests
--------------------------------

The PCE provides dedicated endpoints for reading large object collections through
the API. These collection requests kick off asynchronous jobs on the PCE, and
return the job status URL to be polled until the job is completed.
See the `REST API async overview <https://docs.illumio.com/core/21.5/Content/Guides/rest-api/async-get-collections/overview-of-async-get-requests.htm>`_
for details.

The :meth:`get_async <PolicyComputeEngine._PCEObjectAPI.get_async>`
and :meth:`get_collection <PolicyComputeEngine.get_collection>` methods abstract
the async job poll-wait loop from the caller in order to provide a simpler
synchronous interface for collection requests. If your implementation requires
control over job polling, you can set the poll/wait loop up manually::

    >>> resp = pce.get(headers={'Prefer': 'respond-async'})
    >>> job_poll_url = resp.headers['Location']
    >>> poll_interval = resp.headers['Retry-After']
    >>> while True:
    >>>     resp = pce.get(job_poll_url)
    >>>     poll_result = resp.json()
    >>>     poll_status = poll_result['status']
    >>>     if poll_status == 'done':
    >>>         collection_href = poll_result['result']['href']
    >>>         break
    >>>     elif poll_status == 'failed':
    >>>         raise IllumioException("Job failed: {}".format(poll_result))
    >>>     time.sleep(poll_interval)
    >>> resp = pce.get(collection_href)
    >>> job_results = resp.json()

Container Clusters and Workloads
--------------------------------

The PCE can provide visibility and enforcement for Kubernetes and OpenShift
container orchestration clusters, representing them as :class:`ContainerCluster <illumio.infrastructure.ContainerCluster>`
objects. Container clusters in turn are made up of ``ContainerWorkload`` objects,
which are governed by :class:`ContainerWorkloadProfile <illumio.infrastructure.ContainerWorkloadProfile>`
objects.

While `Kubelink <https://docs.illumio.com/core/21.5/Content/Guides/kubernetes-and-openshift/deployment/deploy-kubelink-in-your-cluster.htm>`_
and `CVEN <https://docs.illumio.com/core/21.5/Content/Guides/kubernetes-and-openshift/deployment/deploy-c-vens-in-your-cluster.htm>`_
deployments must be installed in your Kubernetes or OpenShift cluster
separately, container cluster objects can be created using the **illumio**
library and used to pair these deployments.

.. note::
    When a container cluster is created through the API, the `container_cluster_token`
    is returned in the POST response. This token is only available after the
    object is created and cannot be retrieved via the API: make sure to store
    it in a secure, persistent form such as a Kubernetes or OpenShift Secret.

.. code-block:: python

    >>> container_cluster = ContainerCluster(
    ...     name='CC-GKE-Prod',
    ...     description='Production Kubernetes cluster on GCP'
    ... )
    >>> container_cluster = pce.container_clusters.create(container_cluster)
    >>> container_cluster
    ContainerCluster(
        href='/orgs/1/container_clusters/bba0aa4d-9613-4cf0-b51c-eeb598f2b0f4',
        name='CC-GKE-Prod',
        description='Production Kubernetes cluster on GCP',
        container_cluster_token='1_b7abea42cdade009ab68df7d8e2422749ea38cdbb31d5230bb08258358e58647',
        ...
    )

Virtual Services
----------------

Sometimes workloads may run multiple services or processes, making it difficult
to fit them into the typical labelling workflow. Container cluster nodes are a
good example. For these cases, :class:`VirtualService <illumio.policyobjects.VirtualService>`
objects provide an abstraction for a given service that can be labelled and
bound to one or more workloads. The virtual service object can then be referenced
in rule definitions through the ``resolve_labels_as`` block to apply policy
for the service across all bound workloads.

See the `virtual services section <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/virtual-services.htm>`_
of the Illumio Policy Guide for details.

In the following example, we define two virtual services for a RabbitMQ cluster
serving channels for multiple applications. We'll explore how they can be used
in the sections below.

::

    >>> rabbitmq_svc = pce.services.create(Service(
    ...     name='S-RabbitMQ',
    ...     service_ports=[
    ...         ServicePort(port=5671, to_port=5672, proto='tcp'),   # AMQP/S listeners
    ...         ServicePort(port=15671, to_port=15672, proto='tcp'), # mgmt API/UI, rmqadmin
    ...     ]
    ... ))
    >>> rmq_role_label = pce.labels.create(Label(key='role', value='R-RabbitMQ'))
    >>> notifier_app_label = pce.labels.create(Label(key='app', value='A-Notifier'))
    >>> newsfeed_app_label = pce.labels.create(Label(key='app', value='A-NewsFeed'))
    >>> prod_env_label = pce.labels.create(Label(key='env', value='E-Prod'))
    >>> aws_loc_label = pce.labels.create(Label(key='loc', value='L-AWS'))
    >>> notifier_virtual_service = pce.virtual_services.create(
    ...     VirtualService(
    ...         name='VS-Notifier-RabbitMQ',
    ...         apply_to=ApplyTo.HOST_ONLY,
    ...         service=rabbitmq_svc,
    ...         labels=[rmq_role_label, notifier_app_label, prod_env_label, aws_loc_label]
    ...     )
    ... )
    >>> newsfeed_virtual_service = pce.virtual_services.create(
    ...     VirtualService(
    ...         name='VS-NewsFeed-RabbitMQ',
    ...         apply_to=ApplyTo.HOST_ONLY,
    ...         service=rabbitmq_svc,
    ...         labels=[rmq_role_label, newsfeed_app_label, prod_env_label, aws_loc_label]
    ...     )
    ... )

Service Bindings
################

To associate workloads with a virtual service, you will need to create a :class:`ServiceBinding <illumio.policyobjects.ServiceBinding>`
object. Service bindings link one or more workloads to a virtual service so
they can be referenced in rules, as we'll show in the next section.

.. note::
    Virtual services must be :ref:`provisioned to active state <provisioning>`
    before service bindings can be applied. The example below shows two ways of
    referencing the active HREF, first using a :class:`Reference <illumio.util.Reference>`
    object, and second by updating the virtual service object's ``href`` field
    directly.

We'll extend the example above by binding the RabbitMQ server workload to both
virtual services::

    >>> rmq_workload = pce.workloads.create(Workload(
    ...     name='RabbitMQ Prod', hostname='rmq0.company.com', public_ip='10.0.129.44'
    ... ))
    >>> policy_version = pce.provision_policy_changes(
    ...     change_description="Create RabbitMQ virtual services",
    ...     hrefs=[rabbitmq_svc.href, notifier_virtual_service.href, newsfeed_virtual_service.href]
    ... )
    >>> notifier_vs_active_ref = Reference(
    ...     href=convert_draft_href_to_active(notifier_virtual_service.href)
    ... )
    >>> notifier_binding = ServiceBinding(
    ...     virtual_service=notifier_vs_active_ref,
    ...     workload=rmq_workload,
    ...     port_overrides=[
    ...         PortOverride(
    ...             port=5671, new_port=5673, new_to_port=5674, proto='tcp'
    ...         )
    ...     ]
    ... )
    >>> newsfeed_virtual_service.href = convert_draft_href_to_active(newsfeed_virtual_service.href)
    >>> newsfeed_binding = ServiceBinding(
    ...     virtual_service=newsfeed_virtual_service,
    ...     workload=rmq_workload,
    ...     port_overrides=[
    ...         PortOverride(
    ...             port=5671, new_port=5675, new_to_port=5676, proto='tcp'
    ...         )
    ...     ]
    ... )
    >>> pce.service_bindings.create([notifier_binding, newsfeed_binding])

Writing Rules for Virtual Services
##################################

When using virtual services, your security policy rules will need to be written
slightly differently. Since the virtual service already contains the service
definition, the rule's ``ingress_services`` parameter is left blank. The rule
must also explicitly be configured to resolve labels as virtual services.

See the `virtual service rule writing guide <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/virtual-services.htm#VirtualServicesinRuleWriting>`_
for details.

To illustrate the concept, we'll create a rule set for the NewsFeed application
and add a rule allowing all workloads to reach the RabbitMQ server using the
virtual service we created above::

    >>> newsfeed_rule_set = pce.rule_sets.create(
    ...     RuleSet(
    ...         name='RS-NewsFeed-Prod',
    ...         scopes=[
    ...             LabelSet(labels=[newsfeed_app_label, prod_env_label, aws_loc_label])
    ...         ]
    ...     )
    ... )
    >>> newsfeed_rmq_rule = Rule.build(
    ...     consumers=[AMS],
    ...     providers=[rmq_role_label],
    ...     ingress_services=[],
    ...     resolve_providers_as=[RESOLVE_AS_VIRTUAL_SERVICES]
    ... )
    >>> pce.rules.create(newsfeed_rmq_rule, parent=newsfeed_rule_set)

Traffic Queries
---------------

You can use the PCE API to search the traffic database for flows matching
specific criteria. The traffic query endpoints provide the same interface
as the `Explorer <https://docs.illumio.com/core/21.1/Content/Guides/visualization/explorer/about-explorer.htm>`_
feature in the PCE.

.. note::
    The synchronous traffic query endpoint and :meth:`get_traffic_flows <PolicyComputeEngine.get_traffic_flows>`
    function are deprecated - use the async endpoint and :meth:`get_traffic_flows_async <PolicyComputeEngine.get_traffic_flows_async>`
    function instead. See the `Explorer REST API docs <https://docs.illumio.com/core/21.2/Content/Guides/rest-api/visualization/explorer.htm#Asynchro>`_
    for details.

::

    >>> blocked_rdp_traffic = TrafficQuery.build(
    ...     start_date="2022-07-01T00:00:00Z",
    ...     end_date="2022-08-01T00:00:00Z",
    ...     include_services=[
    ...         {'port': 3389, 'proto': 'tcp'},
    ...         {'port': 3389, 'proto': 'udp'},
    ...     ],
    ...     policy_decisions=['blocked', 'potentially_blocked', 'unknown']
    ... )
    >>> traffic_flows = pce.get_traffic_flows_async(
    ...     query_name='blocked-rdp-traffic-july-22',
    ...     traffic_query=traffic_query
    ... )
