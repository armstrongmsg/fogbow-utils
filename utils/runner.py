from utils.clients.as_client import ASClient
from utils.clients.fhs_client import FHSClient
from utils.clients.test_utils_client import TestUtilsClient
from utils.config.configuration_loader import ConfigurationLoader
from utils.tests.test_loader import TestLoader


class TestRunner:
    def __init__(self):
        configuration = ConfigurationLoader("test.conf")
        as_client = ASClient(configuration.fogbow_ip, configuration.as_port)
        fhs_client = FHSClient(configuration.fogbow_ip, configuration.fhs_port)
        test_utils_client = TestUtilsClient(configuration.fogbow_ip, configuration.test_utils_port)
        test_loader = TestLoader(as_client, fhs_client, test_utils_client, configuration)

        for test_class_name in configuration.test_classes:
            test_class = test_loader.load(test_class_name)
            test_class.test()
