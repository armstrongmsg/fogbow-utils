from utils.tests.fhs.test_ras_invocation import TestRasInvocation
from utils.tests.fhs.test_db_set_up_data import TestDBSetUpData
from utils.tests.fhs.test_db_check_data_after_shutdown import TestDBCheckDataAfterShutdown
from utils.tests.fhs.test_db_add_data_after_shutdown import TestDBAddDataAfterShutdown
from utils.tests.fhs.test_reload import TestReload


class TestLoader:
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        self.as_client = as_client
        self.fhs_client = fhs_client
        self.test_utils_client = test_utils_client
        self.configuration = configuration

    def load(self, test_name):
        # TODO add class loading code

        if test_name == "TestRasInvocation":
            test = TestRasInvocation(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        elif test_name == "TestDBSetUpData":
            test = TestDBSetUpData(self.as_client, self.fhs_client, self.test_utils_client, self.configuration)
        elif test_name == "TestDBCheckDataAfterShutdown":
            test = TestDBCheckDataAfterShutdown(self.as_client, self.fhs_client, self.test_utils_client,
                                                self.configuration)
        elif test_name == "TestDBAddDataAfterShutdown":
            test = TestDBAddDataAfterShutdown(self.as_client, self.fhs_client, self.test_utils_client,
                                              self.configuration)
        elif test_name == "TestReload":
            test = TestReload(self.as_client, self.fhs_client, self.test_utils_client,
                              self.configuration)
        else:
            raise Exception("Invalid test class")

        return test
