from abc import ABCMeta, abstractmethod

import configparser


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


class CloudsTest(FogbowTest):

    def __init__(self, ras_client, token, cloud_names):
        self.ras_client = ras_client
        self.token = token
        self.cloud_names = cloud_names

    def get_test_name(self):
        return "Cloud names"

    def test(self):
        cloud_names_list = []
        for string in self.cloud_names.split(","):
            cloud_names_list.append(string.strip())

        return cloud_names_list == self.ras_client.clouds(self.token)

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
