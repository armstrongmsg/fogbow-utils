from utils.tests.fhs.fhs_test_utils import FHSTest


class TestReload(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        super().__init__(as_client, fhs_client, test_utils_client, configuration)

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestReload"

    def test(self):
        print("### Getting token")
        rewrap_fhs_operator_token = self._get_fhs_operator_token(self.configuration.operator_name_1)
        print(rewrap_fhs_operator_token)

        try:
            self._get_fhs_operator_token(self.configuration.operator_name_2)
        except KeyError:
            pass

        response = self.fhs_client.reload(rewrap_fhs_operator_token)
        print("Response: %s" % str(response))
        print()

        rewrap_fhs_operator_token = self._get_fhs_operator_token(self.configuration.operator_name_1)
        print(rewrap_fhs_operator_token)

        response = self._get_fhs_operator_token(self.configuration.operator_name_2)
        print(response)
