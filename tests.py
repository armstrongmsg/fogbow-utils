from abc import ABCMeta, abstractmethod

import configparser

from fogbow_client import RASClient


class FogbowTest:
    __metaclass__ = ABCMeta

    @abstractmethod
    def test(self):
        pass

    @abstractmethod
    def get_test_name(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass


class CloudTest(FogbowTest):
    __metaclass__ = ABCMeta

    provider_1: str
    provider_2: str
    cloud_names_1: str
    cloud_names_2: str
    ras_client_1: RASClient
    ras_client_2: RASClient
    token: str

    def test(self):
        cloud_names_list_1 = []
        for string in self.cloud_names_1.split(","):
            cloud_names_list_1.append(string.strip())

        cloud_names_list_2 = []
        for string in self.cloud_names_2.split(","):
            cloud_names_list_2.append(string.strip())

        result_test_1 = cloud_names_list_1 == self.ras_client_1.clouds(self.token)
        result_test_2 = cloud_names_list_2 == self.ras_client_2.clouds(self.token)
        result_test_3 = cloud_names_list_1 == self.ras_client_2.clouds_by_provider(self.token, self.provider_1)
        result_test_4 = cloud_names_list_2 == self.ras_client_1.clouds_by_provider(self.token, self.provider_2)

        return result_test_1 and result_test_2 and result_test_3 and result_test_4

    def get_test_name(self):
        pass

    def cleanup(self):
        pass


class CloudsTestBeforeReload(CloudTest):

    def __init__(self, ras_client_1, ras_client_2, token):
        config = configparser.ConfigParser()
        config.read("config.conf")
        self.provider_1 = config.get("clouds_test_before", "provider_1")
        self.provider_2 = config.get("clouds_test_before", "provider_2")
        self.cloud_names_1 = config.get("clouds_test_before", "cloud_names_1")
        self.cloud_names_2 = config.get("clouds_test_before", "cloud_names_2")
        self.ras_client_1 = ras_client_1
        self.ras_client_2 = ras_client_2
        self.token = token

    def get_test_name(self):
        return "Cloud names before reload"

    def cleanup(self):
        pass


class CloudsTestAfterReload(CloudTest):

    def __init__(self, ras_client_1, ras_client_2, token):
        config = configparser.ConfigParser()
        config.read("config.conf")
        self.provider_1 = config.get("clouds_test", "provider_1")
        self.provider_2 = config.get("clouds_test", "provider_2")
        self.cloud_names_1 = config.get("clouds_test", "cloud_names_1")
        self.cloud_names_2 = config.get("clouds_test", "cloud_names_2")
        self.ras_client_1 = ras_client_1
        self.ras_client_2 = ras_client_2
        self.token = token

    def get_test_name(self):
        return "Cloud names after reload"

    def cleanup(self):
        pass


class NetworksTest(FogbowTest):

    def __init__(self, ras_client, token):
        config = configparser.ConfigParser()
        config.read("config.conf")
        self.limit_wait_time = int(config.get("networks_test", "limit_wait_time"))
        self.provider = config.get("networks_test", "provider")
        self.cloud_name = config.get("networks_test", "cloud_name")
        self.name = config.get("networks_test", "name")
        self.cidr = config.get("networks_test", "cidr")
        self.gateway = config.get("networks_test", "gateway")
        self.allocation_mode = config.get("networks_test", "allocation_mode")
        self.ras_client = ras_client
        self.token = token
        self.network_id = None

    def get_test_name(self):
        return "Networks"

    def test(self):
        self.network_id = self.ras_client.create_network_and_wait(self.limit_wait_time,
                                                                  self.token, self.provider,
                                                                  self.cloud_name, self.name,
                                                                  self.cidr, self.gateway,
                                                                  self.allocation_mode)

        success = self.ras_client.network_is_ready(self.token, self.network_id)
        return success

    def cleanup(self):
        self.ras_client.delete_network_and_wait(self.limit_wait_time, self.token, self.network_id)
