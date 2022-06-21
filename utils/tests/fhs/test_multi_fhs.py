from utils.tests.fhs.fhs_test_utils import FHSTest
from utils.clients.fhs_client import FHSClient


class TestMultiFHS(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        super().__init__(as_client, fhs_client, test_utils_client, configuration)

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestMultiFHS"

    def test(self):
        federation_admin = self.configuration.load_federation_admin("admin")
        self.fhs_client = FHSClient(self.configuration.fogbow_ip, self.configuration.fhs_port_2)

        #
        # FhsOperator authentication
        #
        rewrap_fhs_operator_token = self._get_fhs_operator_token(self.configuration.operator_name_1)

        #
        # Federation admin creation and authentication
        #
        print("### Adding new fed admin")
        # TODO constant
        response = self.fhs_client.add_new_fed_admin(rewrap_fhs_operator_token, federation_admin.name,
                                                     federation_admin.email, federation_admin.description,
                                                     federation_admin.enabled,
                                                     {
                                                         "identityPluginClassName":
                                "cloud.fogbow.fhs.core.plugins.authentication.StubFederationAuthenticationPlugin"})
        print("Response: %s\n" % response)
        fed_admin_id = response
        rewrap_fed_admin_1_token = self._get_federation_admin_token(fed_admin_id, federation_admin.name,
                                                                    federation_admin.password)

        print("Checking remote federation")
        response = self.fhs_client.get_remote_federation_list(rewrap_fed_admin_1_token)

        print("Response: %s", str(response))
