import requests
import json


class ASClient:
    def __init__(self, as_host, as_port):
        self.AS_url = "http://%s:%d/as" % (as_host, as_port)
        self.AS_tokens_url = self.AS_url + "/tokens"

    def tokens(self, public_key, username, password):
        payload = {"publicKey": public_key,
                   "credentials": {
                      "username": username,
                      "password": password}
                   }
        headers = {
              'Content-Type': 'application/json'
        }

        response = requests.request("POST", self.AS_tokens_url,
                                    headers=headers, data=json.dumps(payload))

        return json.loads(response.text)["token"]


class RASClient:
    def __init__(self, ras_host, ras_port):
        self.RAS_url = "http://%s:%d/ras" % (ras_host, ras_port)
        self.RAS_clouds_url = self.RAS_url + "/clouds"

    def clouds(self, fogbow_token):
        headers = {'Fogbow-User-Token': fogbow_token}
        response = requests.request("GET", self.RAS_clouds_url, headers=headers)
        return json.loads(response.text)["clouds"]

    def reload(self, fogbow_token):
        headers = {'Fogbow-User-Token': fogbow_token}
        ras_reload_url = self.RAS_url + "/admin/reload"
        requests.request("POST", ras_reload_url, headers=headers)
