.. _usecases:

.. currentmodule:: illumio

Common Use-Cases
================

This document provides example code for several common Policy Compute Engine use-cases.

The PCE connection is omitted below for brevity, check out :ref:`Connect to the PCE <pceconnect>`
in the Quickstart guide to see how to connect to the PCE.

.. note::
    The examples below are intentionally simplified to focus on the PCE
    configuration - error handling, deduplication, helper functions and other
    best practices for production-ready code are left to the reader based on
    application requirements and context.

.. _nanosegmentation:

App Nano-segementation
----------------------

Most enterprise applications are made up of multiple layers, with varying degrees
of deployment complexity. Let's consider a modern web application (for simplicity,
this example ignores many of the network devices involved in routing into and
throughout the data centre).

Application ingress is generally handled through one or more layers of load
balancing to redirect traffic based on geolocation, zone, or traffic distribution.
Many applications will incorporate a reverse proxy to handle application-level
load balancing, traffic redirection, front-end caching, static maintenance or
error pages, header rewriting, and more.

The web application itself may be split into front-end and back-end layers based
on scaling needs. Data is often stored in a distributed SQL database, and often
an additional client-side caching layer is added to improve lookup times and
application responsiveness.

This entire structure is repeated for each deployment environment -- dev, test,
staging, production -- and can be replicated across multiple zones in staging
and production for redundancy, or for parallel deployment models (blue/green).
Additionally, servers may be added or removed to scale the application up or
down and may renew their DHCP leases on a regular basis.

All this adds up to a lot of complexity for networking and security teams to
handle.

With Illumio, we can simplify policy administration using human-readable
abstractions for common elements. The example below shows the step-by-step
process by which we can create all policy objects needed to segment an
application similar to the one described above, restricting communication
to only the necessary workloads, on only the necessary ports.

.. note::
    This example assumes the application workloads already exist and have been
    paired with the PCE. The `Labelling Workloads`_ section below explores these
    concepts in detail.

We'll start by defining all the labels we'll need for this application, and organizing
related labels into `Label Groups <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/labels-and-label-groups.htm#LabelGroups>`_.

.. code-block:: python

    from illumio import *

    # define all the labels we'll need for the application
    web_app_labels = {
        'role': ['R-Web', 'R-HAProxy', 'R-LB', 'R-Redis', 'R-PgSQL'],
        'app': ['A-ShoppingCart'],
        'env': ['E-Dev', 'E-Staging', 'E-Prod'],
        'loc': ['L-US-East-1', 'L-US-East-2', 'L-US-West-1']
    }

    value_to_label_map = {}

    # create all the labels and add them to an index so we can
    # look them up easily later
    for key, label_values in web_app_labels.items():
        for value in label_values:
            label = pce.labels.create(Label(key=key, value=value))
            value_to_label_map[label.value] = label

    # we can treat our dev and staging policy the same way, so
    # let's create a pre-prod label group
    preprod_label_group = pce.label_groups.create(
        LabelGroup(name='LG-E-PreProd', key='env', labels=[
            value_to_label_map['E-Dev'],
            value_to_label_map['E-Staging']
        ])
    )

    # similarly, let's group all our US locations together
    us_label_group = pce.label_groups.create(
        LabelGroup(name='LG-L-US', key='loc', labels=[
            value_to_label_map['L-US-East-1'],
            value_to_label_map['L-US-East-2'],
            value_to_label_map['L-US-West-1'],
        ])
    )

With our labels configured, let's create a `Rule Set <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/create-security-policy/rulesets.htm>`_
for our pre-production environments. If we add, for example, a Test environment
in the future, applying policy will be as simple as updating the pre-prod label
group to include the `E-Test` label.

.. code-block:: python

    preprod_rule_set = pce.rule_sets.create(
        RuleSet(
            name='RS-ShoppingCart-PreProd',
            scopes=[
                # we can define multiple scopes per rule set,
                # but for simplicity we'll stick to one
                LabelSet(
                    labels=[
                        value_to_label_map['A-ShoppingCart'],
                        preprod_label_group,
                        us_label_group
                    ]
                )
            ]
        )
    )

    # now create a similar rule set for production
    prod_rule_set = pce.rule_sets.create(
        RuleSet(
            name='RS-ShoppingCart-Prod',
            scopes=[
                LabelSet(
                    labels=[
                        value_to_label_map['A-ShoppingCart'],
                        value_to_label_map['E-Prod'],
                        us_label_group
                    ]
                )
            ]
        )
    )

We've so far set up labels and label groups to identify our application scope,
as well as rule sets to contain the security policy rules that we'll define in
a moment. First, though, we'll define `Services <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/services.htm>`_
that wrap the ports and protocols our application workloads need to communicate on.

.. code-block:: python

    redis_svc = pce.services.create(
        Service(
            name='S-Redis',
            service_ports=[
                ServicePort(port=6379, proto=convert_protocol('tcp')),
                # you may want to separate the cluster bus port in a real
                # environment, but we're combining them into a single service
                # here for simplicity
                ServicePort(port=16379, proto=convert_protocol('tcp'))
            ]
        )
    )

    web_svc = pce.services.create(
        Service(
            name='S-Web',
            service_ports=[
                ServicePort(port=80, proto=convert_protocol('tcp')),
                ServicePort(port=443, proto=convert_protocol('tcp')),
            ]
        )
    )

    # custom https port for the web application
    shopping_cart_https_svc = pce.services.create(
        Service(
            name='S-ShoppingCartWeb',
            service_ports=[
                ServicePort(port=8443, proto=convert_protocol('tcp'))
            ]
        )
    )

    postgres_svc = pce.services.create(
        Service(
            name='S-PostgreSQL',
            service_ports=[
                ServicePort(port=5432, proto=convert_protocol('tcp'))
            ]
        )
    )

We now have all the building blocks needed to write our security policy
`Rules <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/create-security-policy/rules.htm>`_.
We'll create a rule for each of the connections between workloads within the
scope of our web application. Ingress to the load balancer is defined as an
`extra-scope rule <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/create-security-policy/rules.htm#ExtrascopeRules>`_
so that any IP address can access our application on the web service ports that
we defined above. The remaining connections are defined as
`intra-scope rules <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/create-security-policy/rules.htm#IntrascopeRules>`_
(the default).

.. code-block:: python

    # use the default IP list (0.0.0.0/0 and ::0/0) for ingress
    any_ip_list = pce.get_default_ip_list()

    # now we can define the policy rules between workloads.
    # all rules use default resolution (resolve labels as workloads)
    load_balancer_ingress = Rule.build(
        consumers=[any_ip_list],
        providers=[value_to_label_map['R-LB']],
        ingress_services=[web_svc],
        unscoped_consumers=True  # creates an extra-scope rule
    )

    lb_to_haproxy = Rule.build(
        consumers=[value_to_label_map['R-LB']],
        providers=[value_to_label_map['R-HAProxy']],
        ingress_services=[web_svc]
    )

    proxy_to_web_app = Rule.build(
        consumers=[value_to_label_map['R-HAProxy']],
        providers=[value_to_label_map['R-Web']],
        ingress_services=[shopping_cart_https_svc]
    )

    web_app_to_postgres = Rule.build(
        consumers=[value_to_label_map['R-Web']],
        providers=[value_to_label_map['R-PgSQL']],
        ingress_services=[postgres_svc]
    )

    web_app_to_redis = Rule.build(
        consumers=[value_to_label_map['R-Web']],
        providers=[value_to_label_map['R-Redis']],
        ingress_services=[redis_svc]
    )

    redis_replication = Rule.build(
        consumers=[value_to_label_map['R-Redis']],
        providers=[value_to_label_map['R-Redis']],
        ingress_services=[redis_svc]
    )

    postgres_replication = Rule.build(
        consumers=[value_to_label_map['R-PgSQL']],
        providers=[value_to_label_map['R-PgSQL']],
        ingress_services=[postgres_svc]
    )

    # we're applying the same rules to both rule sets,
    # so we can store them in a list to apply them
    rules = [
        load_balancer_ingress, lb_to_haproxy, proxy_to_web_app,
        web_app_to_redis, web_app_to_postgres,
        redis_replication, postgres_replication
    ]

    # finally, add all the rules to both our pre-prod and prod rule sets
    for rule_set in [preprod_rule_set, prod_rule_set]:
        for rule in rules:
            pce.rules.create(rule, parent=rule_set)

Now that we've created all the necessary policy objects and security rules, we
just need to :ref:`provision <provisioning>` them and move our workloads into
full enforcement for the updated policy to be applied.

.. code-block:: python

    pce.provision_policy_changes(
        change_description="Provision web app nano-segmentation",
        hrefs=[
            preprod_label_group.href, us_label_group.href,
            redis_svc.href, web_svc.href,
            shopping_cart_https_svc.href, postgres_svc.href,
            preprod_rule_set.href, prod_rule_set.href
        ]
    )

.. _ringfencing:

App Ring-fencing
----------------

Ring-fencing is another segmentation approach that requires fewer rules to be
configured, blocking all southbound traffic into the application scope, but
allowing all intra-scope communication between application workloads.

Let's take a look at an example.

.. code-block:: python

    from illumio import *

    elk_labels = {
        'role': ['R-Elasticsearch', 'R-Logstash', 'R-Kibana'],
        'app': ['A-ELK'],
        'env': ['E-Dev', 'E-Prod'],
        'loc': ['L-AWS']
    }

    value_to_label_map = {}

    for key, label_values in elk_labels.items():
        for value in label_values:
            label = pce.labels.create(Label(key=key, value=value))
            value_to_label_map[label.value] = label

As with the nano-segmentation example, we've started by defining the labels
that we'll use to categorize out application. In this case, our labels are
generic enough that we don't need to combine them using label groups.

Next we'll create a rule set for both environments to contain the ring-fence
policy. In this case, since we plan to have the same policy applied to both
our Dev and Prod environments, we'll add them both as scopes to the same rule set.

.. code-block:: python

    ringfence_rule_set = pce.rule_sets.create(
        RuleSet(
            name='RS-ELK',
            scopes=[
                LabelSet(  # Dev scope
                    labels=[
                        value_to_label_map['A-ELK'],
                        value_to_label_map['E-Dev'],
                        value_to_label_map['L-AWS']
                    ]
                ),
                LabelSet(  # Prod scope
                    labels=[
                        value_to_label_map['A-ELK'],
                        value_to_label_map['E-Prod'],
                        value_to_label_map['L-AWS']
                    ]
                )
            ]
        )
    )

Since this is an internal application, we don't want to open it up to the internet.
Instead, we'll define a new `IP List <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/security-policy-objects/ip-lists.htm>`_
that covers our internal network to provide access to the Kibana UI.

.. code-block:: python

    internal_ip_list = pce.ip_lists.create(
        IPList(
            name='IPL-Internal',
            description='Internal network IP subnets',
            ip_ranges=[
                IPRange(from_ip='10.8.0.0/16'),
                IPRange(from_ip='10.2.12.0', to_ip='10.2.19.255'),
                IPRange(from_ip='66.0.0.0/8')
            ],
            fqdns=[
                FQDN(fqdn='*.lab.company.com')
            ]
        )
    )

Now we can configure the ingress services needed for the ELK application.
Kibana will need to expose HTTP/S access, and Logstash will expose its default
port for incoming logs. The ``All Services`` default will be used for all other
intra-scope communication.

.. code-block:: python

    web_svc = pce.services.create(
        Service(
            name='S-Web',
            service_ports=[
                ServicePort(port=80, proto=convert_protocol('tcp')),
                ServicePort(port=443, proto=convert_protocol('tcp'))
            ]
        )
    )

    logstash_svc = pce.services.create(
        Service(
            name='S-Logstash',
            service_ports=[
                ServicePort(port=9600, proto=convert_protocol('tcp'))
            ]
        )
    )

    # get the default global All Services service object
    all_services = pce.get_default_service()

Now all that's left is to define the security policy rules. We'll start by
creating the ingress rules for Kibana and Logstash, and then complete the
ring-fence with an allow-all intra-scope rule.

.. code-block:: python

    kibana_ingress = Rule.build(
        consumers=[internal_ip_list],
        providers=[value_to_label_map['R-Kibana']],
        ingress_services=[web_svc],
        unscoped_consumers=True  # creates an extra-scope rule
    )

    logstash_ingress = Rule.build(
        consumers=[AMS],  # we need all workloads to be able to push to Logstash
        providers=[value_to_label_map['R-Logstash']],
        ingress_services=[logstash_svc],
        unscoped_consumers=True
    )

    # define the rule to create the ring-fence boundary
    allow_all_internal = Rule.build(
        consumers=[AMS],                # all workloads
        providers=[AMS],                # can talk to all workloads
        ingress_services=[all_services] # on all services
    )

    pce.rules.create(kibana_ingress, parent=ringfence_rule_set)
    pce.rules.create(logstash_ingress, parent=ringfence_rule_set)
    pce.rules.create(allow_all_internal, parent=ringfence_rule_set)

Finally, we'll provision the services and rule set to apply them.

.. code-block:: python

    pce.provision_policy_changes(
        change_description="Provision ELK ring-fencing",
        hrefs=[web_svc.href, logstash_svc.href, ringfence_rule_set.href]
    )

.. _workloadlabelling:

Labelling Workloads
-------------------

In the previous examples, we've used labels to define the boundaries of our
applications in rule sets and rules. Let's now revisit labels in the context of
`Workloads <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/workloads/workloads-in-the-pce.htm>`_.

Labels allow us to sort workloads into categories in four pre-defined dimensions:
Role, Application, Environment, and Location. We've seen above how they can be
flexible enough to define and segment complex applications, and we'll show in
the `<Quarantine a Workload>`_ section below how they can represent more abstract
boundaries as well.

Here, we'll show how labels can be applied to workloads, and how to use bulk
operations to make changes to multiple workloads at once.

We'll once again start by creating all the labels we need to categorize our
application workloads.

.. code-block:: python

    from illumio import *

    mlflow_labels = {
        'role': ['R-MLFlowServer', 'R-DB'],
        'app': ['A-MLFlow'],
        'env': ['E-Dev'],
        'loc': ['L-Azure']
    }

    value_to_label_map = {}

    for key, label_values in mlflow_labels.items():
        for value in label_values:
            label = pce.labels.create(Label(key=key, value=value))
            value_to_label_map[label.value] = label

For the purposes of this example, we'll create several
`unmanaged workloads <https://docs.illumio.com/core/21.5/Content/Guides/security-policy/workloads/workload-setup-using-pce-web-console.htm#UnmanagedWorkloads>`_
that we can then update. To do this, we'll take advantage of the
`/workloads/bulk_create <https://docs.illumio.com/core/21.5/Content/Guides/rest-api/workloads/workload-bulk-operations.htm#CreateaCollectionofWorkloads>`_
endpoint to add them all at once. The bulk endpoints can support up to
|BulkChangeLimit| objects in a single call.

.. code-block:: python

    mlflow_server = Workload(name='MLFlow Tracking Server', hostname='mlflow.lab.company.com', public_ip='10.2.14.170')
    mlflow_db0 = Workload(name='MLFlow DB Leader', hostname='db0.lab.company.com', public_ip='10.2.15.13')
    mlflow_db1 = Workload(name='MLFlow DB RO Replica 0', hostname='db1.lab.company.com', public_ip='10.2.15.14')
    mlflow_db2 = Workload(name='MLFlow DB RO Replica 1', hostname='db2.lab.company.com', public_ip='10.2.15.15')

    workloads = pce.workloads.bulk_create([mlflow_server, mlflow_db0, mlflow_db1, mlflow_db2])

To reduce the size of the response, the bulk endpoints only return the HREFs of
the created objects, or any errors that occurred while trying to process the
object change. Because of this, we don't know which HREF in the workloads list
we got back corresponds to each of our servers.

Since the database servers will all use the same labels, we can perform another
bulk operation -- this time using ``/workloads/bulk_update`` -- to change them
all at once. We only have one non-database server, so we can look it up by name.
Once we've updated it individually, we can eliminate its HREF from the workloads
list.

.. code-block:: python

    # do a partial name lookup to find the tracking server workload
    # and update its labels with a normal update call
    mlflow_server = pce.workloads.get(params={'name': 'MLFlow Tracking'})[0]
    pce.workloads.update(mlflow_server, Workload(labels=[
        value_to_label_map['R-MLFlowServer'],
        value_to_label_map['A-MLFlow'],
        value_to_label_map['E-Dev'],
        value_to_label_map['L-Azure']
    ]))

    # eliminate the tracking server HREF from the workloads list
    # and update all the database workloads with the correct labels
    pce.workloads.bulk_update(
        [
            Workload(href=workload['href'], labels=[
                value_to_label_map['R-DB'],
                value_to_label_map['A-MLFlow'],
                value_to_label_map['E-Dev'],
                value_to_label_map['L-Azure']
            ])
            for workload in workloads if workload['href'] != mlflow_server.href
        ]
    )

.. _workloadquarantine:

Quarantine a Workload
---------------------

When responding to a potential breach or investigating possible malicious code
on a workload within the network, it is often prudent to isolate the workload
from the rest of the network to prevent propagation.

This can be accomplished by configuring a set of labels that will act as a
quarantine zone to deny access to and from the labelled workloads.

We'll name these labels ``Quarantine`` below for simplicity, but they could be
anything that makes sense for your organization. We'll also create a special
Role label for the SecOps workloads that will have access to quarantined machines
for analysis.

.. code-block:: python

    from illumio import *

    quarantine_app = pce.labels.create(Label(key='app', value='A-Quarantine'))
    quarantine_env = pce.labels.create(Label(key='env', value='E-Quarantine'))
    quarantine_loc = pce.labels.create(Label(key='loc', value='L-Quarantine'))

    quarantine_labels = [quarantine_app, quarantine_env, quarantine_loc]

    # create a special role for workloads with access to quarantined machines
    secops_role = pce.labels.create(Label(key='role', value='R-SecOpsJumpbox'))

To allow this access, we'll define services for both SSH and RDP connections.

.. code-block:: python

    # create a service definition for SSH - 22 TCP
    ssh_service = pce.services.create(
        Service(
            name='SSH',
            service_ports=[
                ServicePort(port=22, proto=convert_protocol('tcp'))
            ]
        )
    )

    rdp_service = pce.services.create(
        Service(
            name='RDP',
            service_ports=[
                ServicePort(port=3389, proto=convert_protocol('tcp')),
                ServicePort(port=3389, proto=convert_protocol('udp'))
            ]
        )
    )

Now we can create the Quarantine boundary. We'll create extra-scope rules so
any workload with the ``R-SecOpsJumpbox`` role has access.

.. code-block:: python

    quarantine_rule_set = pce.rule_sets.create(
        RuleSet(
            name='RS-Quarantine',
            description='Segmentation rules for quarantining workloads',
            scopes=[
                LabelSet(labels=quarantine_labels)
            ]
        )
    )

    quarantine_allow_secops_ssh = Rule.build(
        providers=[AMS],  # match all workloads within the quarantine scope
        consumers=[secops_role],
        ingress_services=[ssh_service],
        unscoped_consumers=True
    )

    quarantine_allow_secops_rdp = Rule.build(
        providers=[AMS],
        consumers=[secops_role],
        ingress_services=[rdp_service],
        unscoped_consumers=True
    )

    pce.rules.create(quarantine_allow_secops_ssh, parent=quarantine_rule_set)
    pce.rules.create(quarantine_allow_secops_rdp, parent=quarantine_rule_set)

Finally, we'll provision the changes and move an example workload into our
dedicated quarantine zone.

.. code-block:: python

    # provision policy objects to apply the quarantine configuration
    pce.provision_policy_changes(
        'Add quarantine policy object definitions',
        hrefs=[
            ssh_service.href,
            rdp_service.href,
            quarantine_rule_set.href
        ]
    )

    # get the workload that we want to quarantine by its IP address
    infected_workload_ip = '10.8.14.126'
    workloads = pce.workloads.get(params={'ip_address': infected_workload_ip})
    if not workloads:
        raise IllumioException("Failed to find workload with IP address {}".format(infected_workload_ip))
    infected_workload = workloads[0]

    # update the workload labels and make sure it's in full enforcement
    # so our quarantine policy is applied to its firewall
    pce.workloads.update(infected_workload, Workload(
        labels=quarantine_labels,
        enforcement_mode=EnforcementMode.FULL
    ))
