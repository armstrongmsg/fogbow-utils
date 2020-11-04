import requests
import json
import time


class ASClient:
    def __init__(self, as_host, as_port):
        self.AS_url = "http://%s:%d/as" % (as_host, as_port)
        self.AS_tokens_url = self.AS_url + "/tokens"

    def version(self):
        response = requests.request("GET", self.AS_url + "/version")
        return response.text

    def is_active(self):
        try:
            self.version()
            return True
        except:
            return False

    def wait_until_is_active(self):
        while not self.is_active():
            time.sleep(1)

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

    def version(self):
        response = requests.request("GET", self.RAS_url + "/version")
        return response.text

    def is_active(self):
        try:
            self.version()
            return True
        except:
            return False

    def wait_until_is_active(self):
        while not self.is_active():
            time.sleep(1)

    #
    # Clouds
    #

    def clouds(self, fogbow_token):
        headers = {'Fogbow-User-Token': fogbow_token}
        ras_clouds_url = self.RAS_url + "/clouds"
        response = requests.request("GET", ras_clouds_url, headers=headers)
        return json.loads(response.text)["clouds"]

    #
    # Networks
    #

    def get_networks(self, fogbow_token):
        ras_networks_url = self.RAS_url + "/networks"
        ras_networks_status_url = ras_networks_url + "/status"

        headers = {
            'Fogbow-User-Token': fogbow_token
        }

        response = requests.request("GET", ras_networks_status_url, headers=headers)

        return json.loads(response.text)

    def create_network(self, fogbow_token, provider, cloud_name,
                       name, cidr, gateway, allocation_mode):
        ras_networks_url = self.RAS_url + "/networks"

        payload = {
            "provider": provider,
            "cloudName": cloud_name,
            "name": name,
            "cidr": cidr,
            "gateway": gateway,
            "allocationMode": allocation_mode
        }

        headers = {
            'Fogbow-User-Token': fogbow_token,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", ras_networks_url, headers=headers, data=json.dumps(payload))

        return json.loads(response.text)

    def create_network_and_wait(self, limit_wait_time, fogbow_token, provider, cloud_name,
                                name, cidr, gateway, allocation_mode):
        response = self.create_network(fogbow_token, provider, cloud_name, name,
                                       cidr, gateway, allocation_mode)
        network_id = response["id"]
        start = time.time()

        while time.time() - start < limit_wait_time:
            network_state = self.get_network_state(fogbow_token, network_id)
            if network_state in ["READY", "FAILED", "ERROR"]:
                break

            time.sleep(1)

        return network_id

    def delete_network(self, fogbow_token, network_id):
        ras_networks_url = self.RAS_url + "/networks"

        delete_url = ras_networks_url + "/" + network_id

        headers = {
            'Fogbow-User-Token': fogbow_token,
            'Content-Type': 'application/json'
        }

        requests.delete(delete_url, headers=headers)

    def delete_network_and_wait(self, limit_wait_time, fogbow_token, network_id):
        self.delete_network(fogbow_token, network_id)
        start = time.time()

        state = self.get_network_state(fogbow_token, network_id)
        # FIXME check other states
        while time.time() - start < limit_wait_time and\
                state is not None and state != "CLOSED":
            state = self.get_network_state(fogbow_token, network_id)
            time.sleep(1)

    def get_network_state(self, fogbow_token, network_id):
        networks = self.get_networks(fogbow_token)

        for network in networks:
            if network["instanceId"] == network_id:
                return network["state"]
        return None

    def network_is_ready(self, fogbow_token, network_id):
        return self.get_network_state(fogbow_token, network_id) == "READY"

    #
    # Computes
    #

    def create_compute(self, fogbow_token, provider, cloud_name, name,
                       vCPU, ram, disk, image_id, public_key,
                       user_data, network_ids, requirements):
        payload = {
            "provider": provider,
            "cloudName": cloud_name,
            "name": name,
            "vCPU": vCPU,
            "ram": ram,
            "disk": disk,
            "imageId": image_id,
            "publicKey": public_key,
            "userData": user_data,
            "networkIds": network_ids,
            "requirements": requirements
        }

        headers = {'Fogbow-User-Token': fogbow_token}

        ras_create_compute = self.RAS_url + "/computes"
        requests.request("POST", ras_create_compute,
                         headers=headers, data=json.dumps(payload))

    def reload(self, fogbow_token):
        headers = {'Fogbow-User-Token': fogbow_token}
        ras_reload_url = self.RAS_url + "/admin/reload"
        requests.request("POST", ras_reload_url, headers=headers)
