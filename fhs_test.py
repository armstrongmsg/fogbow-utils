import requests
import configparser
import json
import time


def get_content_from_response(response):
    return json.loads(json.loads(response)["responseData"]["content"])


class ConfigurationLoader:
    def __init__(self, configuration_file):
        self.config = configparser.ConfigParser()
        self.config.read(configuration_file)
        
        self.username = self.config["conf"]["username"]
        self.password = self.config["conf"]["password"]
        self.user_public_key = self.config["conf"]["user_public_key"]
        self.fogbow_ip = self.config["conf"]["fogbow_ip"]
        self.as_port = self.config["conf"]["as_port"]
        self.fhs_port = self.config["conf"]["fhs_port"]
        self.test_utils_port = self.config["conf"]["test_utils_port"]
        self.provider = self.config["conf"]["provider"]

        self.network_name = self.config["conf"]["network_name"]
        self.network_cidr = self.config["conf"]["network_cidr"]
        self.network_gateway = self.config["conf"]["network_gateway"]
        self.network_allocation_mode = self.config["conf"]["network_allocation_mode"]
        
        self.compute_name = self.config["conf"]["compute_name"]
        self.compute_vcpu = self.config["conf"]["compute_vcpu"]
        self.compute_ram = self.config["conf"]["compute_ram"]
        self.compute_disk = self.config["conf"]["compute_disk"]
        self.compute_public_key = self.config["conf"]["compute_public_key"]
        self.compute_user_data_file_content = \
            self.config["conf"]["compute_user_data_file_content"]
        self.compute_user_data_file_type = \
            self.config["conf"]["compute_user_data_file_type"]
        self.compute_user_data_tag = self.config["conf"]["compute_user_data_tag"]
        
    def load_federation_admin(self, admin_name):
        admin_username = self.config[admin_name]["username"]
        admin_email = self.config[admin_name]["email"]
        admin_description = self.config[admin_name]["description"]
    
        if self.config["admin"]["enabled"] == "True":
            admin_enabled = True
        else:
            admin_enabled = False
            
        return FederationAdmin(admin_username, admin_email,
                               admin_description, admin_enabled)
        
    def load_federation(self, federation_config_name):
        federation_name = self.config[federation_config_name]["name"]
        
        cloud_names = self.config[federation_config_name]["cloud_names"]

        credentials = {}
        
        for cloud_name in cloud_names.split(","):
            project_name = self.config[cloud_name]["cloud_user_credentials_projectname"]
            password = self.config[cloud_name]["cloud_user_credentials_password"]
            username = self.config[cloud_name]["cloud_user_credentials_username"]
            domain = self.config[cloud_name]["cloud_user_credentials_domain"]
        
            cloud_credentials = {"projectname": project_name, 
                                 "password": password,
                                 "username": username,
                                 "domain": domain}
            
            credentials[cloud_name] = cloud_credentials
        
        federation_metadata = {"credentials": json.dumps(credentials)}
        
        federation_description = self.config[federation_config_name]["description"]
        # federation_enabled = self.config[federation_config_name]["enabled"]
    
        if self.config[federation_config_name]["enabled"] == "True":
            federation_enabled = True
        else:
            federation_enabled = False
            
        return Federation(federation_name, federation_metadata, 
                          federation_description, federation_enabled)
        
    def load_service(self, service_name):
        service_owner = self.config[service_name]["owner"]
        service_endpoint = self.config[service_name]["endpoint"]
        service_type = self.config[service_name]["type"]
        service_invoker_class_name = self.config[service_name]["invoker"]
        service_access_policy_rules = self.config[service_name]["access_rules"]

        service_metadata = {
            "serviceType": service_type,
            "invokerClassName": service_invoker_class_name,
            "accessPolicyRules": service_access_policy_rules
        }
        service_discovery_policy = self.config[service_name]["discovery_policy"]
        service_access_policy = self.config[service_name]["access_policy"]
        
        return FederationService(service_owner, service_endpoint, service_metadata,
                                 service_discovery_policy, service_access_policy)

    
class ASClient:
    def __init__(self, fogbow_ip, as_port):
        self.as_url = "http://%s:%s" % (fogbow_ip, as_port)

    def get_token(self, user_public_key, username, password, federation):
        token_endpoint = self.as_url + "/as/tokens"
        
        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "publicKey": user_public_key,
            "credentials": {
                "username": username,
                "password": password,
                "federationId": federation
            }
        }

        token_response = requests.request("POST", token_endpoint, 
                                          headers=headers, data=json.dumps(body))
        return token_response.json()["token"]


class FederationAdmin:
    def __init__(self, admin_name, admin_email, admin_description, admin_enabled):
        self.name = admin_name
        self.email = admin_email
        self.description = admin_description
        self.enabled = admin_enabled

        
class Federation:
    def __init__(self, name, metadata, description, enabled):
        self.name = name
        self.metadata = metadata
        self.description = description
        self.enabled = enabled


class FederationService:
    def __init__(self, owner, endpoint, metadata, discovery_policy, access_policy):
        self.owner = owner
        self.endpoint = endpoint
        self.metadata = metadata
        self.discovery_policy = discovery_policy
        self.access_policy = access_policy


class FHSClient:
    def __init__(self, fogbow_ip, fhs_port):
        self.fhs_url = "http://%s:%s" % (fogbow_ip, fhs_port)
        
    def get_public_key(self):
        public_key_endpoint = self.fhs_url + "/fhs/publicKey"
        public_key_response = requests.request("GET", public_key_endpoint)
        return public_key_response.json()["publicKey"]
    
    def add_new_fed_admin(self, token, name, email, description, enabled):
        add_new_fed_admin_endpoint = self.fhs_url + "/fhs/FHSOperator/NewFedAdmin"
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "name": name,
            "email": email,
            "description": description, 
            "enabled": enabled
        }
        
        add_new_fed_admin_response = requests.request("POST", add_new_fed_admin_endpoint, 
                                                      headers=headers, data=json.dumps(body))
        
        return add_new_fed_admin_response.json()["memberId"]
    
    def create_federation(self, token, name, metadata, description, enabled):
        create_federation_endpoint = self.fhs_url + "/fhs/Federation"
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "name": name,
            "metadata": metadata,
            "description": description, 
            "enabled": enabled
        }
        
        create_federation_response = requests.request("POST", create_federation_endpoint, 
                                                      headers=headers, data=json.dumps(body))
        
        return create_federation_response.json()["id"]

    def create_attribute(self, token, federation_id, attribute_name):
        create_attribute_endpoint = self.fhs_url + "/fhs/Attributes/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "name": attribute_name
        }

        create_federation_response = requests.request("POST", create_attribute_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return create_federation_response.json()["id"]

    def get_attributes(self, token, federation_id):
        get_attributes_endpoint = self.fhs_url + "/fhs/Attributes/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        create_federation_response = requests.request("GET", get_attributes_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return create_federation_response.json()

    def grant_membership(self, token, federation_id, username, email, description, enabled):
        grant_membership_endpoint = self.fhs_url + "/fhs/Membership/" + federation_id
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "name": username,
            "email": email,
            "description": description, 
            "enabled": enabled
        }
        
        grant_membership_response = requests.request("POST", grant_membership_endpoint, 
                                                     headers=headers, data=json.dumps(body))
        
        return grant_membership_response.json()

    def list_members(self, token, federation_id):
        list_members_endpoint = self.fhs_url + "/fhs/Membership/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        list_members_response = requests.request("GET", list_members_endpoint,
                                                 headers=headers, data=json.dumps(body))

        return list_members_response.json()

    def grant_attribute(self, token, federation_id, member_id, attribute_id):
        grant_attribute_endpoint = self.fhs_url + "/fhs/Authorization/" + \
                                   federation_id + "/" + member_id + "/" + attribute_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        grant_attribute_response = requests.request("PUT", grant_attribute_endpoint,
                                                    headers=headers, data=json.dumps(body))

        return grant_attribute_response.status_code

    def revoke_attribute(self, token, federation_id, member_id, attribute_id):
        revoke_attribute_endpoint = self.fhs_url + "/fhs/Authorization/" + \
                                   federation_id + "/" + member_id + "/" + attribute_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        revoke_attribute_response = requests.request("DELETE", revoke_attribute_endpoint,
                                                     headers=headers, data=json.dumps(body))

        return revoke_attribute_response.status_code

    def register_service(self, token, federation_id, owner_id, endpoint, metadata, 
                         discovery_policy, access_policy):
        register_service_endpoint = self.fhs_url + "/fhs/Services/" + federation_id
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "ownerId": owner_id,
            "endpoint": endpoint,
            "metadata": metadata, 
            "discoveryPolicy": discovery_policy,
            "accessPolicy": access_policy
        }
        
        register_service_response = requests.request("POST", register_service_endpoint, 
                                                     headers=headers, data=json.dumps(body))
        
        return register_service_response.json()["serviceId"]
    
    def invoke_service(self, token, federation_id, service_id, method, invocation_path,
                       invocation_headers, invocation_body):
        invoke_service_endpoint = self.fhs_url + \
                                  "/fhs/Invocation/" + federation_id + "/" + service_id
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "path": invocation_path,
            "headers": invocation_headers,
            "body": invocation_body
        }
        
        invoke_service_response = requests.request(method, invoke_service_endpoint, 
                                                   headers=headers, data=json.dumps(body))
        
        return invoke_service_response.content


class TestUtilsClient:
    def __init__(self, fogbow_ip, test_utils_port):
        self.test_utils_url = "http://%s:%s" % (fogbow_ip, test_utils_port)
    
    def rewrap(self, token, key_to_encrypt):
        rewrap_endpoint = self.test_utils_url + "/utils/rewrap"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        body = {
                "encryptedString": token,
                "encryptKey": key_to_encrypt 
        }
        
        rewrap_response = requests.request("GET", rewrap_endpoint,
                                           headers=headers, data=json.dumps(body))
        return rewrap_response.content.decode("utf-8")


class FHSTest:
    def wait_until_network_is_ready(self, fhs_client, no_federation_fhs_token, 
                                    federated_fhs_token, federation_id,
                                    networks_service_id, network_id):
        network_state = self._get_network_state(fhs_client, no_federation_fhs_token, 
                                                federated_fhs_token, federation_id, 
                                                networks_service_id, network_id)
        
        while network_state != "READY":
            time.sleep(2)
            
            network_state = self._get_network_state(fhs_client, no_federation_fhs_token, 
                                                    federated_fhs_token, federation_id, 
                                                    networks_service_id, network_id)
        
    def _get_network_state(self, fhs_client, no_federation_fhs_token, federated_fhs_token, 
                           federation_id, networks_service_id, network_id):
        response = fhs_client.invoke_service(no_federation_fhs_token, 
                                             federation_id, networks_service_id, 
                                             "GET", ["status"], {"Content-Type": "application/json",
                                                                 "Fogbow-User-Token": federated_fhs_token},
                                             {})
        networks = get_content_from_response(response)

        for network in networks:
            if network["instanceId"] == network_id:
                return network["state"]
            
        return None
    
    def wait_until_compute_is_ready(self, fhs_client, no_federation_fhs_token,
                                    federated_fhs_token, federation_id,
                                    computes_service_id, compute_id):
        compute_state = self._get_compute_state(fhs_client, no_federation_fhs_token, 
                                                federated_fhs_token, federation_id, 
                                                computes_service_id, compute_id)
                
        while compute_state != "READY" and compute_state != "ERROR":
            time.sleep(2)

            compute_state = self._get_compute_state(fhs_client, no_federation_fhs_token, 
                                                    federated_fhs_token, federation_id, 
                                                    computes_service_id, compute_id)
                    
    def _get_compute_state(self, fhs_client, no_federation_fhs_token, 
                           federated_fhs_token, federation_id, 
                           computes_service_id, compute_id):
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             computes_service_id, "GET", ["status"], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        computes = get_content_from_response(response)

        for compute in computes:
            if compute["instanceId"] == compute_id:
                return compute["state"]
        
        return None
    
    def wait_for_compute_deletion(self, fhs_client, no_federation_fhs_token, 
                                  federated_fhs_token, federation_id,
                                  computes_service_id, compute_id):
        while not self._check_if_compute_was_deleted(fhs_client, no_federation_fhs_token, 
                                                     federated_fhs_token, federation_id, 
                                                     computes_service_id, compute_id):
            time.sleep(2)

    def _check_if_compute_was_deleted(self, fhs_client, no_federation_fhs_token, 
                                      federated_fhs_token, federation_id, 
                                      computes_service_id, compute_id):
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             computes_service_id, "GET", ["status"], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        computes = get_content_from_response(response)
            
        for compute in computes:
            if compute["instanceId"] == compute_id:
                return False
            
        return True


class Test1(FHSTest):
    
    def run(self, as_client, fhs_client, test_utils_client, configuration):
        federation_admin = configuration.load_federation_admin("admin")
        federation = configuration.load_federation("federation")
        ras_get_version = configuration.load_service("ras_get_version")
        ras_get_clouds = configuration.load_service("ras_get_clouds")
        ras_get_images = configuration.load_service("ras_get_images")
        ras_networks = configuration.load_service("ras_networks")
        ras_computes = configuration.load_service("ras_computes")
        
        print("### Getting token")
        user_token = as_client.get_token(configuration.user_public_key, 
                                         configuration.username, configuration.password, "")
        print("Token: %s\n" % user_token)
    
        print("### Getting fhs public key") 
        fhs_public_key = fhs_client.get_public_key()
        print("FHS Public key: %s\n" % fhs_public_key)
    
        print("### Rewrapping token")
        no_federation_fhs_token = test_utils_client.rewrap(user_token, fhs_public_key)
        print("Token: %s\n" % no_federation_fhs_token)
    
        print("### Adding new fed admin")
        response = fhs_client.add_new_fed_admin(no_federation_fhs_token, federation_admin.name, 
                                                federation_admin.email, federation_admin.description, 
                                                federation_admin.enabled)
        print("Response: %s\n" % response)
    
        print("### Creating federation")
        federation_id = fhs_client.create_federation(no_federation_fhs_token, federation.name, 
                                                     federation.metadata, federation.description, federation.enabled)
        print("Federation id: %s\n" % federation_id)

        print("### Creating attribute")
        attribute_id = fhs_client.create_attribute(no_federation_fhs_token, federation_id, "attributeName")
        print("Attribute id: %s\n" % attribute_id)

        print("### Getting attributes")
        response = fhs_client.get_attributes(no_federation_fhs_token, federation_id)
        print(response)
        print()

        service_owner_attribute_id = None
        for attribute_map in response:
            if attribute_map["name"] == "serviceOwner":
                service_owner_attribute_id = attribute_map["id"]

        print("### Granting membership")
        response = fhs_client.grant_membership(no_federation_fhs_token, federation_id, 
                                               federation_admin.name, federation_admin.email, 
                                               federation_admin.description, federation_admin.enabled)
        member_id = response["memberId"]
        print("Member id: %s\n" % member_id)

        print("### Granting attribute")
        response = fhs_client.grant_attribute(no_federation_fhs_token, federation_id, member_id,
                                              service_owner_attribute_id)
        print(response)
        print()

        print("### Listing members")
        response = fhs_client.list_members(no_federation_fhs_token, federation_id)
        print(response)
        print()

        # print("### Revoking attribute")
        # response = fhs_client.revoke_attribute(no_federation_fhs_token, federation_id, member_id, attribute_id)
        # print(response)

        print("### Listing members")
        response = fhs_client.list_members(no_federation_fhs_token, federation_id)
        print(response)
        print()

        print("### Registering services")
        get_version_service_id = fhs_client.register_service(no_federation_fhs_token, federation_id, 
                                                             ras_get_version.owner, ras_get_version.endpoint, 
                                                             ras_get_version.metadata, ras_get_version.discovery_policy, 
                                                             ras_get_version.access_policy)
        get_clouds_service_id = fhs_client.register_service(no_federation_fhs_token, federation_id, 
                                                            ras_get_clouds.owner, ras_get_clouds.endpoint, 
                                                            ras_get_clouds.metadata, ras_get_clouds.discovery_policy,
                                                            ras_get_clouds.access_policy)
        get_images_service_id = fhs_client.register_service(no_federation_fhs_token, federation_id,
                                                            ras_get_images.owner, ras_get_images.endpoint,
                                                            ras_get_images.metadata, ras_get_images.discovery_policy,
                                                            ras_get_images.access_policy)
        networks_service_id = fhs_client.register_service(no_federation_fhs_token, federation_id, ras_networks.owner, 
                                                          ras_networks.endpoint, ras_networks.metadata, 
                                                          ras_networks.discovery_policy, ras_networks.access_policy)
        computes_service_id = fhs_client.register_service(no_federation_fhs_token, federation_id, ras_computes.owner, 
                                                          ras_computes.endpoint, ras_computes.metadata, 
                                                          ras_computes.discovery_policy, ras_computes.access_policy)
        print("get version service id: %s" % (get_version_service_id,))
        print("get clouds service id: %s" % (get_clouds_service_id,))
        print("get images service id: %s" % (get_images_service_id,))
        print("networks service id: %s" % (networks_service_id,))
        print("computes service id: %s" % (computes_service_id,))
        print()
        
        federated_token = as_client.get_token(configuration.user_public_key, configuration.username, 
                                              configuration.password, federation_id)
        federated_fhs_token = test_utils_client.rewrap(federated_token, fhs_public_key)
        
        print("### Invoking get version")
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             get_version_service_id, "GET", [], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        print("Response: %s\n" % str(response))
        
        print("### Invoking get clouds")
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             get_clouds_service_id, "GET", [], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        print("Response: %s\n" % str(response))
        
        clouds_list = get_content_from_response(response)["clouds"]
        cloud_name = clouds_list[0]
        
        print("### Invoking get images")
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             get_images_service_id, "GET", [configuration.provider, cloud_name], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        print("Response: %s" % str(response))
        
        images_list = get_content_from_response(response)
        
        image_id = None
        
        for image_dict in images_list:
            if image_dict["name"] == "ubuntu-20.04":
                image_id = image_dict["id"]
                
        print("Selected image: %s\n" % image_id)
        
        print("### Invoking create network")
        
        create_network_body = {
            "provider": configuration.provider, 
            "cloudName": cloud_name,
            "name": configuration.network_name,
            "cidr": configuration.network_cidr,
            "gateway": configuration.network_gateway,
            "allocationMode": configuration.network_allocation_mode
        }
        
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             networks_service_id, "POST", [], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             create_network_body)
        print("Response: %s" % str(response))
        
        network_id = get_content_from_response(response)["id"]
        
        self.wait_until_network_is_ready(fhs_client, no_federation_fhs_token, 
                                         federated_fhs_token, federation_id,
                                         networks_service_id, network_id)
        print("network is ready\n")
        
        print("### Invoking create compute")
        
        create_compute_body = {
            "provider": configuration.provider,
            "cloudName": cloud_name,
            "name": configuration.compute_name,
            "vCPU": configuration.compute_vcpu,
            "ram": configuration.compute_ram,
            "disk": configuration.compute_disk,
            "imageId": image_id,
            "publicKey": configuration.compute_public_key,
            "userData": [{"extraUserDataFileContent": configuration.compute_user_data_file_content, 
                          "extraUserDataFileType": configuration.compute_user_data_file_type,
                          "tag": configuration.compute_user_data_tag}],
            "networkIds": [network_id],
            "requirements": {}
        }
        
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             computes_service_id, "POST", [], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             create_compute_body)
        print("Response: %s" % str(response))
        
        compute_id = get_content_from_response(response)["id"]

        self.wait_until_compute_is_ready(fhs_client, no_federation_fhs_token, 
                                         federated_fhs_token, federation_id,
                                         computes_service_id, compute_id)
                
        print("compute is ready\n")
        
        print("### Invoking delete compute")
        
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             computes_service_id, "DELETE", [compute_id], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        print("Response: %s" % str(response))
        
        print("------ Waiting for compute deletion\n")

        self.wait_for_compute_deletion(fhs_client, no_federation_fhs_token, 
                                       federated_fhs_token, federation_id,
                                       computes_service_id, compute_id)
        
        print("### Invoking delete network")
        
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, 
                                             networks_service_id, "DELETE", [network_id], 
                                             {"Content-Type": "application/json",
                                              "Fogbow-User-Token": federated_fhs_token},
                                             {})
        print("Response: %s\n" % str(response))


class TestRunner:
    def __init__(self):
        configuration = ConfigurationLoader("fhs_test.conf")
    
        as_client = ASClient(configuration.fogbow_ip, configuration.as_port)
        fhs_client = FHSClient(configuration.fogbow_ip, configuration.fhs_port)
        test_utils_client = TestUtilsClient(configuration.fogbow_ip, configuration.test_utils_port)

        Test1().run(as_client, fhs_client, test_utils_client, configuration)


if __name__ == "__main__":
    TestRunner()
    
