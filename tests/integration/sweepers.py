"""This module defines teardown functions for integration tests.


"""
from illumio import PolicyComputeEngine, IllumioException


class Sweeper:
    def __init__(self, pce: PolicyComputeEngine, session_identifier) -> None:
        self.pce = pce
        self.session_identifier = session_identifier

    def _sweep(self, api, lookup='external_data_set'):
        try:
            objects = api.get(params={lookup: self.session_identifier})
            for o in objects:
                api.delete(o.href)
        except IllumioException:
            pass

    def _sweep_container_clusters(self):
        self._sweep(self.pce.container_clusters, lookup='name')

    def _sweep_enforcement_boundaries(self):
        self._sweep(self.pce.enforcement_boundaries, lookup='name')

    def _sweep_ip_lists(self):
        self._sweep(self.pce.ip_lists)

    def _sweep_label_groups(self):
        self._sweep(self.pce.label_groups)

    def _sweep_labels(self):
        self._sweep(self.pce.labels)

    def _sweep_pairing_profiles(self):
        self._sweep(self.pce.pairing_profiles)

    def _sweep_rule_sets(self):
        self._sweep(self.pce.rule_sets)

    def _sweep_services(self):
        self._sweep(self.pce.services)

    def _sweep_virtual_services(self):
        self._sweep(self.pce.virtual_services)

    def _sweep_workloads(self):
        self._sweep(self.pce.workloads)

    def sweep(self):
        [getattr(self, fn)() for fn in dir(self) if fn.startswith('_sweep_')]
