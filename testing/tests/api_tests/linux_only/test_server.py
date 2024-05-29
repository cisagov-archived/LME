import json
import time
import warnings

import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import os

from api_tests.helpers import make_request, load_json_schema, get_latest_winlogbeat_index, post_request

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

current_script_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_script_path)


def convertJsonFileToString(file_path):
    with open(file_path, "r") as file:
        return file.read()


@pytest.fixture(autouse=True)
def suppress_insecure_request_warning():
    warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)



def test_winlogbeat_insert(es_host, es_port, username, password):
    # Computer software overview-> Filter Hosts
    url = f"https://{es_host}:{es_port}"
    filter_hosts_query = load_json_schema(f"{current_script_dir}/queries/filter_hosts.json")
    first_response = make_request(f"{url}/winlogbeat-*/_search", username, password, filter_hosts_query)

    latest_index = get_latest_winlogbeat_index(es_host, es_port, username, password)

    fixture = load_json_schema(f"{current_script_dir}/fixtures/hosts.json")

    ans =  post_request(f"{url}/{latest_index}/_doc", username, password, fixture)
    time.sleep(5)

    second_response = make_request(f"{url}/winlogbeat-*/_search", username, password, filter_hosts_query)

    second_response_loaded = second_response.json()

    print(f"Response: {second_response_loaded}")



def test_elastic_root(es_host, es_port, username, password):
    url = f"https://{es_host}:{es_port}"
    response = make_request(url, username, password)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    body = response.json()

    assert body["name"] == "es01", f"Expected 'es01', got {body['name']}"
    assert (
            body["cluster_name"] == "loggingmadeeasy-es"
    ), f"Expected 'loggingmadeeasy-es', got {body['cluster_name']}"
    assert (
            body["version"]["number"] == "8.11.1"
    ), f"Expected '8.11.1', got {body['version']['number']}"
    assert (
            body["version"]["build_flavor"] == "default"
    ), f"Expected 'default', got {body['version']['build_flavor']}"
    assert (
            body["version"]["build_type"] == "docker"
    ), f"Expected 'docker', got {body['version']['build_type']}"
    assert (
            body["version"]["lucene_version"] == "9.8.0"
    ), f"Expected '9.8.0', got {body['version']['lucene_version']}"
    assert (
            body["version"]["minimum_wire_compatibility_version"] == "7.17.0"
    ), f"Expected '7.17.0', got {body['version']['minimum_wire_compatibility_version']}"
    assert (
            body["version"]["minimum_index_compatibility_version"] == "7.0.0"
    ), f"Expected '7.0.0', got {body['version']['minimum_index_compatibility_version']}"

    # Validating JSON Response schema
    schema = load_json_schema(f"{current_script_dir}/schemas/es_root.json")
    validate(instance=response.json(), schema=schema)


def test_elastic_indices(es_host, es_port, username, password):
    url = f"https://{es_host}:{es_port}/_cat/indices/"
    response = make_request(url, username, password)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert (
            "green open .internal.alerts-observability.logs.alerts-default" in response.text
    )
    assert (
            "green open .internal.alerts-observability.uptime.alerts-default"
            in response.text
    )
    assert (
            "green open .internal.alerts-ml.anomaly-detection.alerts-default"
            in response.text
    )
    assert (
            "green open .internal.alerts-observability.slo.alerts-default" in response.text
    )
    assert (
            "green open .internal.alerts-observability.apm.alerts-default" in response.text
    )
    assert (
            "green open .internal.alerts-observability.metrics.alerts-default"
            in response.text
    )
    assert (
            "green open .kibana-observability-ai-assistant-conversations" in response.text
    )
    assert "green open winlogbeat" in response.text
    assert (
            "green open .internal.alerts-observability.threshold.alerts-default"
            in response.text
    )
    assert "green open .kibana-observability-ai-assistant-kb" in response.text
    assert "green open .internal.alerts-security.alerts-default" in response.text
    assert "green open .internal.alerts-stack.alerts-default" in response.text
