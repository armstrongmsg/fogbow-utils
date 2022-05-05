import json
import requests


class TestUtilsClient:
    def __init__(self, fogbow_ip, test_utils_port):
        self.test_utils_url = "http://%s:%s" % (fogbow_ip, test_utils_port)

    def rewrap(self, token, key_to_encrypt):
        rewrap_endpoint = self.test_utils_url + "/utils/rewrap"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "encryptedString": token,
            "encryptKey": key_to_encrypt
        }

        rewrap_response = requests.request("GET", rewrap_endpoint,
                                           headers=headers, data=json.dumps(body))
        return rewrap_response.content.decode("utf-8")
