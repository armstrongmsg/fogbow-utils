from utils.tests.fhs.fhs_test_utils import FHSTest


class TestDBCheckDataAfterShutdown(FHSTest):
    def __init__(self, as_client, fhs_client, test_utils_client, configuration):
        super().__init__(as_client, fhs_client, test_utils_client, configuration)

    def cleanup(self):
        pass

    def get_test_name(self):
        return "TestDBCheckDataAfterShutdown"
    
    def test(self):
        federation_admin = self.configuration.load_federation_admin("admin")
        service_owner_1 = self.configuration.load_user("service_owner_1")

        rewrap_fhs_operator_token = self._get_fhs_operator_token(self.configuration.operator_name_1)

        response = self.fhs_client.list_fed_admins(rewrap_fhs_operator_token)
        print("Response: %s\n" % str(response))
        print()

        fed_admin_id = response[0]["memberId"]

        response = self.fhs_client.list_federation_instances(rewrap_fhs_operator_token)
        print("Response: %s\n" % str(response))
        print()

        rewrap_fed_admin_1_token = self._get_federation_admin_token(fed_admin_id, federation_admin.name,
                                                                    federation_admin.password)

        response = self.fhs_client.get_federations(rewrap_fed_admin_1_token, fed_admin_id)
        print("Response: %s\n" % str(response))
        print()

        federation_id = response[0]["id"]

        response = self.fhs_client.get_federation_info(rewrap_fed_admin_1_token, federation_id, fed_admin_id)
        print("Response: %s\n" % str(response))
        print()

        response = self.fhs_client.get_attributes(rewrap_fed_admin_1_token, federation_id)
        print("Response: %s\n" % str(response))
        print()

        print("Checking members")
        response = self.fhs_client.list_members(rewrap_fed_admin_1_token, federation_id)
        print("Response: %s\n" % str(response))
        print()

        service_owner_id = None

        for member in response:
            if "serviceOwner" in member["attributes"]:
                service_owner_id = member["memberId"]

        rewrap_service_owner_1_token = self._get_member_token(federation_id, service_owner_id, service_owner_1.name,
                                                              service_owner_1.password)

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
