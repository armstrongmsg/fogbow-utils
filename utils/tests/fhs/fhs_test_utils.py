from utils.tests.tests import FogbowTest

import json
import time


def get_content_from_response(response):
    return json.loads(json.loads(response)["responseData"]["content"])


class FHSTest(FogbowTest):
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
