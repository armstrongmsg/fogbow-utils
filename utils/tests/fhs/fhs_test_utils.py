from utils.tests.tests import FogbowTest
from utils.tools.logger import Log

import json
import time


LOGGER = Log("TestLog", "test.log")


def get_content_from_response(response):
    return json.loads(json.loads(response)["responseData"]["content"])


class FHSTest(FogbowTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        self.as_client = as_client
        self.fhs_client = fhs_client
        self.test_utils_client = test_utils_client
        self.configuration = configuration

    def setup(self):
        pass

    def cleanup(self):
        pass

    def get_test_name(self):
        pass

    def test(self):
        pass

    def wait_until_network_is_ready(self, fhs_client, no_federation_fhs_token,
                                    federated_fhs_token, federation_id,
                                    networks_service_id, network_id):
        network_state = self._get_network_state(fhs_client, no_federation_fhs_token,
                                                federated_fhs_token, federation_id,
                                                networks_service_id, network_id)

        while network_state != "READY":
            time.sleep(2)

            network_state = self._get_network_state(fhs_client, no_federation_fhs_token,
                                                    federated_fhs_token, federation_id,
                                                    networks_service_id, network_id)

    def _get_network_state(self, fhs_client, no_federation_fhs_token, federated_fhs_token,
                           federation_id, networks_service_id, network_id):
        response = fhs_client.invoke_service(no_federation_fhs_token,
                                             federation_id, networks_service_id,
                                             "GET", ["status"], {"Content-Type": "application/json",
                                                                 "Fogbow-User-Token": federated_fhs_token},
                                             {})
        networks = get_content_from_response(response)

        for network in networks:
            if network["instanceId"] == network_id:
                return network["state"]

        return None

    def wait_until_compute_is_ready(self, fhs_client, no_federation_fhs_token,
                                    federated_fhs_token, federation_id,
                                    computes_service_id, compute_id):
        compute_state = self._get_compute_state(fhs_client, no_federation_fhs_token,
                                                federated_fhs_token, federation_id,
                                                computes_service_id, compute_id)

        while compute_state != "READY" and compute_state != "ERROR":
            time.sleep(2)

            compute_state = self._get_compute_state(fhs_client, no_federation_fhs_token,
                                                    federated_fhs_token, federation_id,
                                                    computes_service_id, compute_id)

    def _get_compute_state(self, fhs_client, no_federation_fhs_token,
                           federated_fhs_token, federation_id,
                           computes_service_id, compute_id):
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                             computes_service_id, "GET", ["status"],
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        computes = get_content_from_response(response)

        for compute in computes:
            if compute["instanceId"] == compute_id:
                return compute["state"]

        return None

    def wait_for_compute_deletion(self, fhs_client, no_federation_fhs_token,
                                  federated_fhs_token, federation_id,
                                  computes_service_id, compute_id):
        while not self._check_if_compute_was_deleted(fhs_client, no_federation_fhs_token,
                                                     federated_fhs_token, federation_id,
                                                     computes_service_id, compute_id):
            time.sleep(2)

    def _check_if_compute_was_deleted(self, fhs_client, no_federation_fhs_token,
                                      federated_fhs_token, federation_id,
                                      computes_service_id, compute_id):
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                             computes_service_id, "GET", ["status"],
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        computes = get_content_from_response(response)

        for compute in computes:
            if compute["instanceId"] == compute_id:
                return False

        return True

    def wait_for_network_deletion(self, fhs_client, no_federation_fhs_token,
                                  federated_fhs_token, federation_id,
                                  networks_service_id, network_id):
        while not self._check_if_network_was_deleted(fhs_client, no_federation_fhs_token,
                                                     federated_fhs_token, federation_id,
                                                     networks_service_id, network_id):
            time.sleep(2)

    def _check_if_network_was_deleted(self, fhs_client, no_federation_fhs_token,
                                      federated_fhs_token, federation_id,
                                      networks_service_id, network_id):
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                             networks_service_id, "GET", ["status"],
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        networks = get_content_from_response(response)

        for network in networks:
            if network["instanceId"] == network_id:
                return False

        return True

    def _get_fhs_operator_token(self, operator_name):
        LOGGER.log("### Getting token")

        operator = self.configuration.load_fhs_operator(operator_name)

        credentials_fhs_operator = {
            "userPublicKey": operator.public_key,
            "username": operator.username,
            "password": operator.password
        }

        fhs_operator_token = self.fhs_client.login_operator(operator.id, credentials_fhs_operator)

        LOGGER.log("### Getting fhs public key")
        fhs_public_key = self.fhs_client.get_public_key()
        LOGGER.log("FHS Public key: %s\n" % fhs_public_key)

        LOGGER.log("### Rewrapping token")
        rewrap_fhs_operator_token = self.test_utils_client.rewrap(fhs_operator_token, fhs_public_key)
        LOGGER.log("Token: %s\n" % rewrap_fhs_operator_token)

        return rewrap_fhs_operator_token

    def _get_federation_admin_token(self, fed_admin_id, federation_admin_name, federation_admin_password):
        credentials_fed_amin = {
            "userPublicKey": self.configuration.user_public_key,
            "username": federation_admin_name,
            "password": federation_admin_password
        }

        fed_admin_1_token = self.fhs_client.login_federation_admin(fed_admin_id, credentials_fed_amin)

        fhs_public_key = self.fhs_client.get_public_key()
        rewrap_fed_admin_1_token = self.test_utils_client.rewrap(fed_admin_1_token, fhs_public_key)
        LOGGER.log("Token: %s\n" % rewrap_fed_admin_1_token)

        return rewrap_fed_admin_1_token

    def _get_member_token(self, federation_id, member_id, username, password):
        credentials_service_owner = {
            "userPublicKey": self.configuration.user_public_key,
            "username": username,
            "password": password
        }

        member_token = self.fhs_client.login(federation_id, member_id, credentials_service_owner)
        fhs_public_key = self.fhs_client.get_public_key()
        rewrap_member_token = self.test_utils_client.rewrap(member_token, fhs_public_key)
        LOGGER.log("Token: %s\n" % rewrap_member_token)

        return rewrap_member_token
