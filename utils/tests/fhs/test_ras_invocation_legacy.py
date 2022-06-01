from utils.tests.fhs.fhs_test_utils import FHSTest
from utils.tests.fhs.fhs_test_utils import get_content_from_response


class TestRasInvocation(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        super().__init__(as_client, fhs_client, test_utils_client, configuration)

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestRasInvocation"

    def test(self):
        federation_admin = self.configuration.load_federation_admin("admin")
        federation = self.configuration.load_federation("federation")
        ras_get_version = self.configuration.load_service("ras_get_version")
        ras_get_clouds = self.configuration.load_service("ras_get_clouds")
        ras_get_images = self.configuration.load_service("ras_get_images")
        ras_networks = self.configuration.load_service("ras_networks")
        ras_computes = self.configuration.load_service("ras_computes")

        print("### Getting token")
        user_token = self.as_client.tokens(self.configuration.user_public_key,
                                           self.configuration.username,
                                           self.configuration.password, "")
        print("Token: %s\n" % user_token)

        print("### Getting fhs public key")
        fhs_public_key = self.fhs_client.get_public_key()
        print("FHS Public key: %s\n" % fhs_public_key)

        print("### Rewrapping token")
        no_federation_fhs_token = self.test_utils_client.rewrap(user_token, fhs_public_key)
        print("Token: %s\n" % no_federation_fhs_token)

        print("### Adding new fed admin")
        response = self.fhs_client.add_new_fed_admin(no_federation_fhs_token, federation_admin.name,
                                                     federation_admin.email, federation_admin.description,
                                                     federation_admin.enabled)
        print("Response: %s\n" % response)

        print("### Creating federation")
        federation_id = self.fhs_client.create_federation(no_federation_fhs_token, federation.name,
                                                          federation.metadata, federation.description,
                                                          federation.enabled)
        print("Federation id: %s\n" % federation_id)

        print("### Creating attribute")
        attribute_id = self.fhs_client.create_attribute(no_federation_fhs_token, federation_id, "attributeName")
        print("Attribute id: %s\n" % attribute_id)

        print("### Getting attributes")
        response = self.fhs_client.get_attributes(no_federation_fhs_token, federation_id)
        print(response)
        print()

        service_owner_attribute_id = None
        for attribute_map in response:
            if attribute_map["name"] == "serviceOwner":
                service_owner_attribute_id = attribute_map["id"]

        print("### Granting membership")
        response = self.fhs_client.grant_membership(no_federation_fhs_token, federation_id,
                                                    federation_admin.name, federation_admin.email,
                                                    federation_admin.description, federation_admin.enabled)
        member_id = response["memberId"]
        print("Member id: %s\n" % member_id)

        print("### Granting attribute")
        response = self.fhs_client.grant_attribute(no_federation_fhs_token, federation_id, member_id,
                                                   service_owner_attribute_id)
        print(response)
        print()

        print("### Listing members")
        response = self.fhs_client.list_members(no_federation_fhs_token, federation_id)
        print(response)
        print()

        # print("### Revoking attribute")
        # response = fhs_client.revoke_attribute(no_federation_fhs_token, federation_id, member_id, attribute_id)
        # print(response)

        print("### Listing members")
        response = self.fhs_client.list_members(no_federation_fhs_token, federation_id)
        print(response)
        print()

        print("### Registering services")
        get_version_service_id = self.fhs_client.register_service(no_federation_fhs_token, federation_id,
                                                                  ras_get_version.owner,
                                                                  ras_get_version.endpoint,
                                                                  ras_get_version.metadata,
                                                                  ras_get_version.discovery_policy,
                                                                  ras_get_version.access_policy)
        get_clouds_service_id = self.fhs_client.register_service(no_federation_fhs_token, federation_id,
                                                                 ras_get_clouds.owner,
                                                                 ras_get_clouds.endpoint,
                                                                 ras_get_clouds.metadata,
                                                                 ras_get_clouds.discovery_policy,
                                                                 ras_get_clouds.access_policy)
        get_images_service_id = self.fhs_client.register_service(no_federation_fhs_token, federation_id,
                                                                 ras_get_images.owner, ras_get_images.endpoint,
                                                                 ras_get_images.metadata,
                                                                 ras_get_images.discovery_policy,
                                                                 ras_get_images.access_policy)
        networks_service_id = self.fhs_client.register_service(no_federation_fhs_token, federation_id,
                                                               ras_networks.owner,
                                                               ras_networks.endpoint,
                                                               ras_networks.metadata,
                                                               ras_networks.discovery_policy,
                                                               ras_networks.access_policy)
        computes_service_id = self.fhs_client.register_service(no_federation_fhs_token, federation_id,
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

        federated_token = self.as_client.tokens(self.configuration.user_public_key, self.configuration.username,
                                                self.configuration.password, federation_id)
        federated_fhs_token = self.test_utils_client.rewrap(federated_token, fhs_public_key)

        print("### Invoking get version")
        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  get_version_service_id, "GET", [],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token}, {})
        print("Response: %s\n" % str(response))

        print("### Invoking get clouds")
        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  get_clouds_service_id, "GET", [],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token}, {})
        print("Response: %s\n" % str(response))

        clouds_list = get_content_from_response(response)["clouds"]
        cloud_name = clouds_list[0]

        print("### Invoking get images")
        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  get_images_service_id, "GET",
                                                  [self.configuration.provider, cloud_name],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token}, {})
        print("Response: %s" % str(response))

        images_list = get_content_from_response(response)

        image_id = None

        for image_dict in images_list:
            if image_dict["name"] == "ubuntu-20.04":
                image_id = image_dict["id"]

        print("Selected image: %s\n" % image_id)

        print("### Invoking create network")

        create_network_body = {
            "provider": self.configuration.provider,
            "cloudName": cloud_name,
            "name": self.configuration.network_name,
            "cidr": self.configuration.network_cidr,
            "gateway": self.configuration.network_gateway,
            "allocationMode": self.configuration.network_allocation_mode
        }

        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  networks_service_id, "POST", [],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token},
                                                  create_network_body)
        print("Response: %s" % str(response))

        network_id = get_content_from_response(response)["id"]

        self.wait_until_network_is_ready(self.fhs_client, no_federation_fhs_token,
                                         federated_fhs_token, federation_id,
                                         networks_service_id, network_id)
        print("network is ready\n")

        print("### Invoking create compute")

        create_compute_body = {
            "provider": self.configuration.provider,
            "cloudName": cloud_name,
            "name": self.configuration.compute_name,
            "vCPU": self.configuration.compute_vcpu,
            "ram": self.configuration.compute_ram,
            "disk": self.configuration.compute_disk,
            "imageId": image_id,
            "publicKey": self.configuration.compute_public_key,
            "userData": [{"extraUserDataFileContent": self.configuration.compute_user_data_file_content,
                          "extraUserDataFileType": self.configuration.compute_user_data_file_type,
                          "tag": self.configuration.compute_user_data_tag}],
            "networkIds": [network_id],
            "requirements": {}
        }

        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  computes_service_id, "POST", [],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token},
                                                  create_compute_body)
        print("Response: %s" % str(response))

        compute_id = get_content_from_response(response)["id"]

        self.wait_until_compute_is_ready(self.fhs_client, no_federation_fhs_token,
                                         federated_fhs_token, federation_id,
                                         computes_service_id, compute_id)

        print("compute is ready\n")

        print("### Invoking delete compute")

        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  computes_service_id, "DELETE", [compute_id],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token}, {})
        print("Response: %s" % str(response))

        print("------ Waiting for compute deletion\n")

        self.wait_for_compute_deletion(self.fhs_client, no_federation_fhs_token,
                                       federated_fhs_token, federation_id,
                                       computes_service_id, compute_id)

        print("### Invoking delete network")

        response = self.fhs_client.invoke_service(no_federation_fhs_token, federation_id,
                                                  networks_service_id, "DELETE", [network_id],
                                                  {"Content-Type": "application/json",
                                                   "Fogbow-User-Token": federated_fhs_token}, {})
        print("Response: %s\n" % str(response))

    def run(self):
        pass
