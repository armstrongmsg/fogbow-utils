import time

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
        service_owner_1 = self.configuration.load_user("service_owner_1")
        ras_get_version = self.configuration.load_service("ras_get_version")
        common_user_1 = self.configuration.load_user("common_user_1")

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

        response = self.fhs_client.grant_membership(rewrap_fed_admin_2_token, federation_id_to_join,
                                                    service_owner_1.name, service_owner_1.authentication_properties,
                                                    service_owner_1.email, service_owner_1.description,
                                                    service_owner_1.enabled)
        service_owner_id = response["memberId"]
        print("Member id: %s\n" % service_owner_id)

        print("### Getting attributes")
        response = self.fhs_client.get_attributes(rewrap_fed_admin_2_token, federation_id_to_join)
        print(response)
        print()

        service_owner_attribute_id = None
        for attribute_map in response:
            if attribute_map["name"] == "serviceOwner":
                service_owner_attribute_id = attribute_map["id"]

        print("### Granting attribute")
        response = self.fhs_client.grant_attribute(rewrap_fed_admin_2_token, federation_id_to_join, service_owner_id,
                                                   service_owner_attribute_id)

        LOGGER.log("Response: %s" % str(response))

        rewrap_service_owner_1_token = self._get_member_token(federation_id_to_join, service_owner_id, service_owner_1.name,
                                                              service_owner_1.password)

        print("### Registering services")
        get_version_service_id = self.fhs_client.register_service(rewrap_service_owner_1_token, federation_id_to_join,
                                                                  ras_get_version.owner,
                                                                  ras_get_version.endpoint,
                                                                  ras_get_version.metadata,
                                                                  ras_get_version.discovery_policy,
                                                                  ras_get_version.access_policy)

        LOGGER.log("Response: %s" % str(get_version_service_id))

        time.sleep(20)

        self.fhs_client = FHSClient(self.configuration.fogbow_ip, self.configuration.fhs_port)

        response = self.fhs_client.list_members(rewrap_fed_admin_1_token, federation_id_to_join)

        LOGGER.log("Response: %s" % str(response))

        response = self.fhs_client.get_federation_info(rewrap_fed_admin_1_token, federation_id_to_join, "")

        LOGGER.log("Response: %s" % str(response))

        response = self.fhs_client.grant_membership(rewrap_fed_admin_1_token, federation_id_to_join,
                                         common_user_1.name, common_user_1.authentication_properties,
                                         common_user_1.email, common_user_1.description,
                                         common_user_1.enabled)

        LOGGER.log("Response: %s" % str(response))

        common_user_1_id = response["memberId"]
        print("Member id: %s\n" % common_user_1_id)

        rewrap_common_user_1_token = self._get_member_token(federation_id, common_user_1_id, common_user_1.name,
                                                            common_user_1.password)

        response = self.fhs_client.discover_services(rewrap_common_user_1_token, federation_id_to_join, "aaa")

        LOGGER.log("Response: %s" % str(response))
