import re
import json
import pytest
import requests_mock
from illumio.pce import PolicyComputeEngine
from illumio.policyobjects import Label, LabelGroup, ServicePort
from illumio.rules import Rule, RuleSet
from illumio.workloads import Workload
from illumio.explorer import TrafficQuery, TrafficFlow

@pytest.fixture
def traffic_flow_json():
    return [
        {
            "src": {"ip": "10.0.0.1"},
            "dst": {"ip": "10.0.0.2", "workload": {"href": "/orgs/1/workloads/1", "name": "web"}},
            "service": {"port": 80, "proto": 6},
            "policy_decision": "allowed",
            "flow_direction": "inbound",
            "transmission": "unicast"
        }
    ]

def test_rule_sets_get_async(pce, requests_mock):
    """Verifies pce.rule_sets.get_async() logic."""
    # The library prepends /api/v2 and potentially /orgs/1
    # get_async calls get_collection with include_org=False
    # Location header is passed directly to pce.get()
    
    requests_mock.get(re.compile('/sec_policy/draft/rule_sets'), status_code=202, headers={
        'Location': '/jobs/1',
        'Retry-After': '0'
    })
    
    # jobs/1 with include_org=True (default in pce.get) becomes orgs/1/jobs/1
    requests_mock.get(re.compile('/orgs/1/jobs/1'), json={
        "status": "done",
        "result": {"href": "/sec_policy/draft/rule_sets/download"}
    })
    
    # result['href'] for policy objects is used in pce.get(collection_href)
    # /sec_policy/draft/rule_sets/download with include_org=True becomes orgs/1/sec_policy/draft/rule_sets/download
    requests_mock.get(re.compile('/orgs/1/sec_policy/draft/rule_sets/download'), json=[
        {"href": "/orgs/1/sec_policy/draft/rule_sets/1", "name": "RS-1"}
    ])
    
    results = pce.rule_sets.get_async()
    assert len(results) == 1
    assert isinstance(results[0], RuleSet)

def test_rules_get_async(pce, requests_mock):
    """Verifies pce.rules.get_async() logic."""
    requests_mock.get(re.compile('/sec_policy/draft/sec_rules'), status_code=202, headers={
        'Location': '/jobs/2',
        'Retry-After': '0'
    })
    
    requests_mock.get(re.compile('/orgs/1/jobs/2'), json={
        "status": "done",
        "result": {"href": "/sec_policy/draft/sec_rules/download"}
    })
    
    requests_mock.get(re.compile('/orgs/1/sec_policy/draft/sec_rules/download'), json=[
        {"href": "/orgs/1/sec_policy/draft/rule_sets/1/sec_rules/1"}
    ])
    
    try:
        results = pce.rules.get_async()
        assert len(results) == 1
        assert isinstance(results[0], Rule)
    except Exception as e:
        import traceback
        traceback.print_exc()
        pytest.fail(f"rules.get_async failed: {e}")

def test_traffic_flows_async(pce, requests_mock, traffic_flow_json):
    """Verifies pce.get_traffic_flows_async() logic."""
    # get_traffic_flows_async calls post with include_org=True
    requests_mock.post(re.compile('/orgs/1/traffic_flows/async_queries'), json={
        "href": "/orgs/1/traffic_flows/async_queries/123"
    }, status_code=202)
    
    # _async_poll calls self.get(location) which defaults include_org=True
    # But since /orgs/1/... starts with orgs/, it won't be prepended again.
    requests_mock.get(re.compile('/orgs/1/traffic_flows/async_queries/123'), json={
        "status": "completed",
        "result": "/orgs/1/traffic_flows/async_queries/123/download"
    })
    
    requests_mock.get(re.compile('/orgs/1/traffic_flows/async_queries/123/download'), json=traffic_flow_json)
    
    traffic_query = TrafficQuery.build(
        start_date="2022-01-01T00:00:00Z",
        end_date="2022-01-02T00:00:00Z"
    )
    
    flows = pce.get_traffic_flows_async(query_name="test-query", traffic_query=traffic_query)
    assert len(flows) == 1
    assert isinstance(flows[0], TrafficFlow)
    
    traffic_query = TrafficQuery.build(
        start_date="2022-01-01T00:00:00Z",
        end_date="2022-01-02T00:00:00Z"
    )
    
    flows = pce.get_traffic_flows_async(query_name="test-query", traffic_query=traffic_query)
    
    assert len(flows) == 1
    assert isinstance(flows[0], TrafficFlow)
    assert flows[0].dst.workload.name == "web"

def test_workload_crud(pce, requests_mock):
    """Verifies Workload CRUD logic."""
    requests_mock.get(re.compile('/workloads'), json=[
        {"href": "/orgs/1/workloads/1", "name": "workload-1"}
    ])
    
    workloads = pce.workloads.get()
    assert len(workloads) == 1
    assert isinstance(workloads[0], Workload)

def test_label_crud(pce, requests_mock):
    """Verifies Label CRUD logic."""
    # Create
    requests_mock.post(re.compile('/labels'), json={"href": "/orgs/1/labels/1", "key": "app", "value": "test"}, status_code=201)
    label = pce.labels.create(Label(key="app", value="test"))
    assert label.href == "/orgs/1/labels/1"
    
    # Update
    requests_mock.put(re.compile('/orgs/1/labels/1'), status_code=204)
    label.value = "updated"
    pce.labels.update(label.href, label)
    
    # Delete
    requests_mock.delete(re.compile('/orgs/1/labels/1'), status_code=204)
    pce.labels.delete(label.href)
