from utils.clients.as_client import ASClient
from utils.clients.fhs_client import FHSClient
from utils.clients.test_utils_client import TestUtilsClient
from utils.config.configuration_loader import ConfigurationLoader

from utils.tests.fhs.test1 import Test1


class TestRunner:
    def __init__(self):
        configuration = ConfigurationLoader("test.conf")
    
        as_client = ASClient(configuration.fogbow_ip, configuration.as_port)
        fhs_client = FHSClient(configuration.fogbow_ip, configuration.fhs_port)
        test_utils_client = TestUtilsClient(configuration.fogbow_ip, configuration.test_utils_port)

        Test1(as_client, fhs_client, test_utils_client, configuration).test()
