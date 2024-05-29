import json

import requests
from requests.auth import HTTPBasicAuth


def make_request(url, username, password, body=None):
    auth = HTTPBasicAuth(username, password)
    headers = {"Content-Type": "application/json"}

    if body:
        response = requests.post(
            url, auth=auth, verify=False, data=json.dumps(body), headers=headers
        )
    else:
        response = requests.get(url, auth=auth, verify=False)

    return response

def get_latest_winlogbeat_index(hostname, port, username, password):
    url = f"https://{hostname}:{port}/_cat/indices/winlogbeat-*?h=index&s=index:desc&format=json"
    response = make_request(url, username, password)
    
    if response.status_code == 200:
        indices = json.loads(response.text)
        if indices:
            latest_index = indices[0]["index"]
            return latest_index
        else:
            print("No winlogbeat indices found.")
    else:
        print(f"Error retrieving winlogbeat indices. Status code: {response.status_code}")
    
    return None

def post_request(url, username, password, body):
    auth = HTTPBasicAuth(username, password)
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(
        url,
        auth=auth,
        verify=False,
        data=json.dumps(body),
        headers=headers
    )
    
    return response

def load_json_schema(file_path):
    with open(file_path, "r") as file:
        return json.load(file)
