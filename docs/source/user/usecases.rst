.. _usecases:

.. currentmodule:: illumio

Common Use-Cases
================

This document provides example code for several common PCE use-cases.

.. note::
    The implementations below are intentionally simplified to focus on the PCE
    configuration - error handling, deduplication, helper functions and other
    best practices for production-ready code are left to the reader based on
    application requirements and context.

App Micro-segementation
-----------------------

<<< TODO >>>

App Ring-fence
--------------

<<< TODO >>>

Quarantine a Workload
---------------------

When responding to a potential breach or investigating possible malicious code
on a workload within the network, it is often prudent to isolate the workload
from the rest of the network to prevent propagation.

This can be accomplished by configuring a set of labels that will act as a
quarantine zone to deny access to and from the labelled workloads.

.. code-block:: python
    :linenos:

    from illumio import (
        PolicyComputeEngine,
        IllumioException,
        Label,
        Service,
        ServicePort,
        RuleSet,
        Rule,
        Workload,
        EnforcementMode,
        AMS,
        convert_protocol
    )

    pce = PolicyComputeEngine('my.pce.com', port=443, org_id=1)
    pce.set_credentials('api_key', 'api_secret')

    if not pce.check_connection():
        raise IllumioException("Failed to connect to the PCE")

    # create labels to use for quarantine
    quarantine_app = pce.labels.create(Label(key='app', value='A-Quarantine'))
    quarantine_env = pce.labels.create(Label(key='env', value='E-Quarantine'))
    quarantine_loc = pce.labels.create(Label(key='loc', value='L-Quarantine'))

    quarantine_labels = [quarantine_app, quarantine_env, quarantine_loc]

    # create a rule set to house quarantine security rules
    quarantine_rule_set = pce.rule_sets.create(
        RuleSet(
            name='RS-Quarantine',
            description='Segmentation rules for quarantining workloads',
            scopes=[
                LabelSet(labels=quarantine_labels)
            ]
        )
    )

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

    # create a special role for workloads with access to quarantined machines
    secops_role = pce.labels.create(Label(key='role', value='R-SecOpsJumpbox'))

    # create security policy rules that establish our quarantine perimeter
    quarantine_allow_secops_ssh = Rule.build(
        providers=[AMS],  # match all workloads within the quarantine scope
        consumers=[secops_role],
        ingress_services=[ssh_service],
        resolve_consumers_as=['workloads'],
        resolve_providers_as=['workloads'],
        enabled=True
    )

    pce.rules.create(quarantine_allow_secops_ssh, parent=quarantine_rule_set)

    quarantine_allow_secops_rdp = Rule.build(
        providers=[AMS],
        consumers=[secops_role],
        ingress_services=[rdp_service],
        resolve_consumers_as=['workloads'],
        resolve_providers_as=['workloads'],
        enabled=True
    )

    pce.rules.create(quarantine_allow_secops_rdp, parent=quarantine_rule_set)

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
    infected_workload_ip = '10.10.14.126'
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
