from utils.clients.as_client import ASClient
from utils.clients.fhs_client import FHSClient
from utils.clients.test_utils_client import TestUtilsClient
from utils.config.configuration_loader import ConfigurationLoader

from utils.tests.fhs.test1 import Test1
from utils.tests.fhs.test2 import Test2
from utils.tests.fhs.test_db_before import TestDBBefore
from utils.tests.fhs.test_db_after import TestDBAfter


class TestRunner:
    def __init__(self):
        configuration = ConfigurationLoader("test.conf")
    
        as_client = ASClient(configuration.fogbow_ip, configuration.as_port)
        fhs_client = FHSClient(configuration.fogbow_ip, configuration.fhs_port)
        test_utils_client = TestUtilsClient(configuration.fogbow_ip, configuration.test_utils_port)

        # TestDBBefore(as_client, fhs_client, test_utils_client, configuration).test()
        TestDBAfter(as_client, fhs_client, test_utils_client, configuration).test()
