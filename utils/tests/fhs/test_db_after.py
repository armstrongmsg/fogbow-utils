from utils.tests.fhs.fhs_test_utils import FHSTest


class TestDBAfter(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        self.as_client = as_client
        self.fhs_client = fhs_client
        self.test_utils_client = test_utils_client
        self.configuration = configuration

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestDBAfter"
    
    def test(self):
        federation_admin = self.configuration.load_federation_admin("admin")
        service_owner_1 = self.configuration.load_user("service_owner_1")

        print("### Getting fhs public key")
        fhs_public_key = self.fhs_client.get_public_key()
        print("FHS Public key: %s\n" % fhs_public_key)

        credentials_fhs_operator = {
            "userPublicKey": self.configuration.user_public_key,
            "username": self.configuration.username,
            "password": self.configuration.password
        }

        fhs_operator_token = self.fhs_client.login_operator("armstrongmsg", credentials_fhs_operator)

        print("### Rewrapping token")
        rewrap_fhs_operator_token = self.test_utils_client.rewrap(fhs_operator_token, fhs_public_key)
        print("Token: %s\n" % rewrap_fhs_operator_token)

        response = self.fhs_client.list_fed_admins(rewrap_fhs_operator_token)
        print("Response: %s\n" % str(response))
        print()

        fed_admin_id = response[0]["memberId"]

        credentials_fed_amin = {
            "userPublicKey": self.configuration.user_public_key,
            "username": federation_admin.name,
            "password": federation_admin.password
        }

        fed_admin_1_token = self.fhs_client.login_federation_admin(fed_admin_id, credentials_fed_amin)

        rewrap_fed_admin_1_token = self.test_utils_client.rewrap(fed_admin_1_token, fhs_public_key)
        print("Token: %s\n" % rewrap_fed_admin_1_token)

        response = self.fhs_client.get_federations(rewrap_fed_admin_1_token, fed_admin_id)
        print("Response: %s\n" % str(response))
        print()

        federation_id = response[0]["id"]

        print("Checking members")
        response = self.fhs_client.list_members(rewrap_fed_admin_1_token, federation_id)
        print("Response: %s\n" % str(response))
        print()

        service_owner_id = None

        for member in response:
            if "serviceOwner" in member["attributes"]:
                service_owner_id = member["memberId"]

        credentials_service_owner = {
            "userPublicKey": self.configuration.user_public_key,
            "username": service_owner_1.name,
            "password": service_owner_1.password
        }

        service_owner_1_token = self.fhs_client.login(federation_id, service_owner_id, credentials_service_owner)

        rewrap_service_owner_1_token = self.test_utils_client.rewrap(service_owner_1_token, fhs_public_key)
        print("Token: %s\n" % rewrap_service_owner_1_token)

        print("Getting services")
        response = self.fhs_client.get_services(rewrap_service_owner_1_token, federation_id, service_owner_id)
        print("Response: %s", str(response))

        for service in response:
            response2 = self.fhs_client.get_service(rewrap_service_owner_1_token, federation_id,
                                                    service_owner_id, service["serviceId"])
            print(str(response2))

        response = self.fhs_client.get_attributes(rewrap_fed_admin_1_token, federation_id)
        print(response)
        print()
