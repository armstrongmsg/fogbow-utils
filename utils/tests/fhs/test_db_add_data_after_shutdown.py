from utils.tests.fhs.fhs_test_utils import FHSTest


class TestDBAddDataAfterShutdown(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        self.as_client = as_client
        self.fhs_client = fhs_client
        self.test_utils_client = test_utils_client
        self.configuration = configuration

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestDBAddDataAfterShutdown"

    def test(self):
        federation_admin_2 = self.configuration.load_federation_admin("admin2")
        federation_2 = self.configuration.load_federation("federation2")
        service_owner_2 = self.configuration.load_user("service_owner_2")
        common_user_1 = self.configuration.load_user("common_user_1")
        ras_get_version = self.configuration.load_service("ras_get_version")
        ras_get_clouds = self.configuration.load_service("ras_get_clouds")
        ras_get_images = self.configuration.load_service("ras_get_images")
        ras_networks = self.configuration.load_service("ras_networks")
        ras_computes = self.configuration.load_service("ras_computes")

        #
        # FhsOperator authentication
        #

        print("### Getting token")

        credentials_fhs_operator = {
            "userPublicKey": self.configuration.user_public_key,
            "username": self.configuration.username,
            "password": self.configuration.password
        }

        fhs_operator_token = self.fhs_client.login_operator("armstrongmsg", credentials_fhs_operator)

        print("### Getting fhs public key")
        fhs_public_key = self.fhs_client.get_public_key()
        print("FHS Public key: %s\n" % fhs_public_key)

        print("### Rewrapping token")
        rewrap_fhs_operator_token = self.test_utils_client.rewrap(fhs_operator_token, fhs_public_key)
        print("Token: %s\n" % rewrap_fhs_operator_token)

        #
        # Federation admin creation and authentication
        #

        print("### Adding new fed admin")
        # TODO constant
        response = self.fhs_client.add_new_fed_admin(rewrap_fhs_operator_token, federation_admin_2.name,
                                                     federation_admin_2.email, federation_admin_2.description,
                                                     federation_admin_2.enabled,
                                                     {
                                                         "identityPluginClassName":
                                "cloud.fogbow.fhs.core.plugins.authentication.StubFederationAuthenticationPlugin"})
        print("Response: %s\n" % response)
        fed_admin_id = response

        credentials_fed_amin = {
            "userPublicKey": self.configuration.user_public_key,
            "username": federation_admin_2.name,
            "password": federation_admin_2.password
        }

        fed_admin_1_token = self.fhs_client.login_federation_admin(fed_admin_id, credentials_fed_amin)

        rewrap_fed_admin_1_token = self.test_utils_client.rewrap(fed_admin_1_token, fhs_public_key)
        print("Token: %s\n" % rewrap_fed_admin_1_token)

        #
        # Federation creation
        #

        print("### Creating federation")
        federation_id = self.fhs_client.create_federation(rewrap_fed_admin_1_token, federation_2.name,
                                                          federation_2.metadata, federation_2.description,
                                                          federation_2.enabled)
        print("Federation id: %s\n" % federation_id)

        #
        # Attributes management
        #

        print("### Attributes before creation")
        response = self.fhs_client.get_attributes(rewrap_fed_admin_1_token, federation_id)
        print(response)
        print()

        print("### Creating attribute")
        attribute_id = self.fhs_client.create_attribute(rewrap_fed_admin_1_token, federation_id, "attributeName2")
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
                                                    service_owner_2.name, service_owner_2.authentication_properties,
                                                    service_owner_2.email, service_owner_2.description,
                                                    service_owner_2.enabled)
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

        credentials_service_owner = {
            "userPublicKey": self.configuration.user_public_key,
            "username": service_owner_2.name,
            "password": service_owner_2.password
        }

        service_owner_1_token = self.fhs_client.login(federation_id, service_owner_id, credentials_service_owner)

        rewrap_service_owner_1_token = self.test_utils_client.rewrap(service_owner_1_token, fhs_public_key)
        print("Token: %s\n" % rewrap_service_owner_1_token)

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

        credentials_common_user_1 = {
            "userPublicKey": self.configuration.user_public_key,
            "username": common_user_1.name,
            "password": common_user_1.password
        }

        common_user_1_token = self.fhs_client.login(federation_id, common_user_1_id, credentials_common_user_1)

        rewrap_common_user_1_token = self.test_utils_client.rewrap(common_user_1_token, fhs_public_key)
        print("Token: %s\n" % rewrap_common_user_1_token)
