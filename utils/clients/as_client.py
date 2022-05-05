import json
import requests
import time


class ASClient:
    def __init__(self, as_host, as_port):
        self.AS_url = "http://%s:%s/as" % (as_host, as_port)
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

    def tokens(self, public_key, username, password, federation):
        payload = {"publicKey": public_key,
                   "credentials": {
                      "username": username,
                      "password": password,
                      "federationId": federation}
                   }
        headers = {
              'Content-Type': 'application/json'
        }

        response = requests.request("POST", self.AS_tokens_url,
                                    headers=headers, data=json.dumps(payload))

        return json.loads(response.text)["token"]
