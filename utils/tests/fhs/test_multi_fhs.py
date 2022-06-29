from utils.tests.fhs.fhs_test_utils import FHSTest
from utils.clients.fhs_client import FHSClient
from utils.tools.fhs_bootstrap import FHSBootstrap
from utils.tools.logger import Log


LOGGER = Log("TestLog", "test.log")


class TestMultiFHS(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        super().__init__(as_client, fhs_client, test_utils_client, configuration)
        self.fhs_1 = None
        self.fhs_2 = None

    def setup(self):
        self.fhs_1 = FHSBootstrap(self.configuration.as_build_path, self.configuration.ras_build_path,
                                  self.configuration.ms_build_path, self.configuration.fhs_port,
                                  self.configuration.fhs_name_1, self.configuration.fhs_project_path,
                                  self.configuration.fhs_bootstrap_workspace)
        self.fhs_1.deploy()

    def cleanup(self):
        self.fhs_1.cleanup()
        self.fhs_2.cleanup()

    def get_test_name(self):
        return "TestMultiFHS"

    def test(self):
        federation_admin = self.configuration.load_federation_admin("admin")
        federation = self.configuration.load_federation("federation")

        #
        # FhsOperator authentication
        #
        rewrap_fhs_operator_token = self._get_fhs_operator_token(self.configuration.operator_name_1)

        #
        # Federation admin creation and authentication
        #
        LOGGER.log("### Adding new fed admin")
        # TODO constant
        response = self.fhs_client.add_new_fed_admin(rewrap_fhs_operator_token, federation_admin.name,
                                                     federation_admin.email, federation_admin.description,
                                                     federation_admin.enabled,
                                                     {
                                                         "identityPluginClassName":
                                                             "cloud.fogbow.fhs.core.plugins.authentication.StubFederationAuthenticationPlugin"})
        LOGGER.log("Response: %s\n" % response)
        fed_admin_id = response
        rewrap_fed_admin_1_token = self._get_federation_admin_token(fed_admin_id, federation_admin.name,
                                                                    federation_admin.password)

        #
        # Federation creation
        #

        LOGGER.log("### Creating federation")
        federation_id = self.fhs_client.create_federation(rewrap_fed_admin_1_token, federation.name,
                                                          federation.metadata, federation.description,
                                                          federation.enabled)
        LOGGER.log("Federation id: %s\n" % federation_id)

        LOGGER.log("### Checking remote admins allowed in federation")

        response = self.fhs_client.get_join_requests(rewrap_fed_admin_1_token)
        LOGGER.log("Allowed admins: %s" % response)

        LOGGER.log("### Adding allowed remote admin")
        response = self.fhs_client.remote_join_grant(rewrap_fed_admin_1_token, "federation_admin_2",
                                                     "member2.lsd.ufcg.edu.br", federation_id)
        LOGGER.log("Response: %s" % response)

        response = self.fhs_client.get_join_requests(rewrap_fed_admin_1_token)
        LOGGER.log("Allowed admins: %s" % response)

        #
        # Starting FHS 2
        #
        LOGGER.log("### Starting FHS 2")
        self.fhs_2 = FHSBootstrap(self.configuration.as_build_path, self.configuration.ras_build_path,
                                  self.configuration.ms_build_path, self.configuration.fhs_port_2,
                                  self.configuration.fhs_name_2, self.configuration.fhs_project_path,
                                  self.configuration.fhs_bootstrap_workspace)
        self.fhs_2.prepare_config()
        self.fhs_2.start()

        federation_admin_2 = self.configuration.load_federation_admin("admin2")
        self.fhs_client = FHSClient(self.configuration.fogbow_ip, self.configuration.fhs_port_2)

        #
        # FhsOperator authentication
        #
        rewrap_fhs_operator_token = self._get_fhs_operator_token(self.configuration.operator_name_1)

        #
        # Federation admin creation and authentication
        #
        LOGGER.log("### Adding new fed admin")
        # TODO constant
        response = self.fhs_client.add_new_fed_admin(rewrap_fhs_operator_token, federation_admin_2.name,
                                                     federation_admin_2.email, federation_admin_2.description,
                                                     federation_admin_2.enabled,
                                                     {
                                                         "identityPluginClassName":
                                "cloud.fogbow.fhs.core.plugins.authentication.StubFederationAuthenticationPlugin"})
        LOGGER.log("Response: %s\n" % response)
        fed_admin_id = response
        rewrap_fed_admin_2_token = self._get_federation_admin_token(fed_admin_id, federation_admin_2.name,
                                                                    federation_admin_2.password)

        LOGGER.log("Checking remote federation")
        response = self.fhs_client.get_remote_federation_list(rewrap_fed_admin_2_token)

        LOGGER.log("Response: %s" % str(response))
        federation_id_to_join = response[0]["id"]

        response = self.fhs_client.join_remote_federation(rewrap_fed_admin_2_token, federation_id_to_join)
        LOGGER.log("Response: %s" % str(response))

        response = self.fhs_client.get_federations(rewrap_fed_admin_2_token, federation_admin_2.name)
        LOGGER.log("Response: %s" % str(response))

        response = self.fhs_client.list_federation_instances(rewrap_fhs_operator_token)
        LOGGER.log("Response: %s" % str(response))
