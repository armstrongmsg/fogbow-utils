from utils.tests.fhs.fhs_test_utils import FHSTest


class TestDBSetUpData(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        super().__init__(as_client, fhs_client, test_utils_client, configuration)

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestDBSetUpData"

    def test(self):
        federation_admin = self.configuration.load_federation_admin("admin")
        federation = self.configuration.load_federation("federation")
        service_owner_1 = self.configuration.load_user("service_owner_1")
        common_user_1 = self.configuration.load_user("common_user_1")
        ras_get_version = self.configuration.load_service("ras_get_version")
        ras_get_clouds = self.configuration.load_service("ras_get_clouds")
        ras_get_images = self.configuration.load_service("ras_get_images")
        ras_networks = self.configuration.load_service("ras_networks")
        ras_computes = self.configuration.load_service("ras_computes")

        #
        # FhsOperator authentication
        #
        rewrap_fhs_operator_token = self._get_fhs_operator_token()

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

        #
        # Federation creation
        #

        print("### Creating federation")
        federation_id = self.fhs_client.create_federation(rewrap_fed_admin_1_token, federation.name,
                                                          federation.metadata, federation.description,
                                                          federation.enabled)
        print("Federation id: %s\n" % federation_id)

        #
        # Attributes management
        #

        print("### Attributes before creation")
        response = self.fhs_client.get_attributes(rewrap_fed_admin_1_token, federation_id)
        print(response)
        print()

        print("### Creating attribute")
        attribute_id = self.fhs_client.create_attribute(rewrap_fed_admin_1_token, federation_id, "attributeName")
        print("Attribute id: %s\n" % attribute_id)

        print("### Getting attributes")
        response = self.fhs_client.get_attributes(rewrap_fed_admin_1_token, federation_id)
        print(response)
        print()

        service_owner_attribute_id = None
        for attribute_map in response:
            if attribute_map["name"] == "serviceOwner":
                service_owner_attribute_id = attribute_map["id"]

        print("### Deleting attribute")
        response = self.fhs_client.delete_attribute(rewrap_fed_admin_1_token, federation_id, attribute_id)
        print(response)
        print()

        print("### Checking attribute deletion")
        response = self.fhs_client.get_attributes(rewrap_fed_admin_1_token, federation_id)
        print(response)
        print()

        #
        # Creating a service owner
        #

        print("### Granting membership")
        response = self.fhs_client.grant_membership(rewrap_fed_admin_1_token, federation_id,
                                                    service_owner_1.name, service_owner_1.authentication_properties,
                                                    service_owner_1.email, service_owner_1.description,
                                                    service_owner_1.enabled)
        service_owner_id = response["memberId"]
        print("Member id: %s\n" % service_owner_id)

        print("### Granting attribute")
        response = self.fhs_client.grant_attribute(rewrap_fed_admin_1_token, federation_id, service_owner_id,
                                                   service_owner_attribute_id)
        print(response)
        print()

        #
        # Registering services
        #

        rewrap_service_owner_1_token = self._get_member_token(federation_id, service_owner_id, service_owner_1.name,
                                                              service_owner_1.password)

        print("### Registering services")
        get_version_service_id = self.fhs_client.register_service(rewrap_service_owner_1_token, federation_id,
                                                                  ras_get_version.owner,
                                                                  ras_get_version.endpoint,
                                                                  ras_get_version.metadata,
                                                                  ras_get_version.discovery_policy,
                                                                  ras_get_version.access_policy)

        get_clouds_service_id = self.fhs_client.register_service(rewrap_service_owner_1_token, federation_id,
                                                                 ras_get_clouds.owner,
                                                                 ras_get_clouds.endpoint,
                                                                 ras_get_clouds.metadata,
                                                                 ras_get_clouds.discovery_policy,
                                                                 ras_get_clouds.access_policy)

        get_images_service_id = self.fhs_client.register_service(rewrap_service_owner_1_token, federation_id,
                                                                 ras_get_images.owner, ras_get_images.endpoint,
                                                                 ras_get_images.metadata,
                                                                 ras_get_images.discovery_policy,
                                                                 ras_get_images.access_policy)

        networks_service_id = self.fhs_client.register_service(rewrap_service_owner_1_token, federation_id,
                                                               ras_networks.owner,
                                                               ras_networks.endpoint,
                                                               ras_networks.metadata,
                                                               ras_networks.discovery_policy,
                                                               ras_networks.access_policy)

        computes_service_id = self.fhs_client.register_service(rewrap_service_owner_1_token, federation_id,
                                                               ras_computes.owner,
                                                               ras_computes.endpoint, ras_computes.metadata,
                                                               ras_computes.discovery_policy,
                                                               ras_computes.access_policy)

        print("get version service id: %s" % (get_version_service_id,))
        print("get clouds service id: %s" % (get_clouds_service_id,))
        print("get images service id: %s" % (get_images_service_id,))
        print("networks service id: %s" % (networks_service_id,))
        print("computes service id: %s" % (computes_service_id,))
        print()

        print("Getting services")
        response = self.fhs_client.get_services(rewrap_service_owner_1_token, federation_id, service_owner_id)
        print("Response: %s", str(response))

        #
        # Creating a regular member
        #

        print("### Granting membership")
        response = self.fhs_client.grant_membership(rewrap_fed_admin_1_token, federation_id,
                                                    common_user_1.name, common_user_1.authentication_properties,
                                                    common_user_1.email, common_user_1.description,
                                                    common_user_1.enabled)
        common_user_1_id = response["memberId"]
        print("Member id: %s\n" % common_user_1_id)

        rewrap_common_user_1_token = self._get_member_token(federation_id, common_user_1_id, common_user_1.name,
                                                            common_user_1.password)
