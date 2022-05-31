from utils.tests.fhs.test1 import Test1
from utils.tests.fhs.test2 import Test2
from utils.tests.fhs.test_db_before import TestDBBefore
from utils.tests.fhs.test_db_after import TestDBAfter
from utils.tests.fhs.test_db_after2 import TestDBAfter2


class TestLoader:
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        self.as_client = as_client
        self.fhs_client = fhs_client
        self.test_utils_client = test_utils_client
        self.configuration = configuration

    def load(self, test_name):
        # TODO add class loading code

        if test_name == "Test1":
            test = Test1(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        elif test_name == "Test2":
            test = Test2(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        elif test_name == "TestDBBefore":
            test = TestDBBefore(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        elif test_name == "TestDBAfter":
            test = TestDBAfter(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        elif test_name == "TestDBAfter2":
            test = TestDBAfter2(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        else:
            raise Exception("Invalid test class")

        return test
