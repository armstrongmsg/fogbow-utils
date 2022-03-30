import requests
import configparser
import json
from google.protobuf.internal import test_util

class Configuration_Loader:
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
        
    def load_federation_admin(self, admin_name):
        admin_username = self.config[admin_name]["username"]
        admin_email = self.config[admin_name]["email"]
        admin_description = self.config[admin_name]["description"]
    
        if self.config["admin"]["enabled"] == "True":
            admin_enabled = True
        else:
            admin_enabled = False
            
        return Federation_Admin(admin_username, admin_email, 
                                admin_description, admin_enabled)
        
    def load_federation(self, federation_config_name):
        federation_name = self.config[federation_config_name]["name"]
        federation_description = self.config[federation_config_name]["description"]
        federation_enabled = self.config[federation_config_name]["enabled"]
    
        if self.config[federation_config_name]["enabled"] == "True":
            federation_enabled = True
        else:
            federation_enabled = False
            
        return Federation(federation_name, federation_description, 
                          federation_enabled)
        
    def load_service(self, service_name):
        service_owner = self.config[service_name]["owner"]
        service_endpoint = self.config[service_name]["endpoint"]
        service_type = self.config[service_name]["type"]
        service_metadata = {"serviceType":service_type}
        service_discovery_policy = self.config[service_name]["discovery_policy"]
        service_access_policy = self.config[service_name]["access_policy"]
        
        return Federation_Service(service_owner, service_endpoint, service_metadata, 
                                  service_discovery_policy, service_access_policy)
        
class AS_Client:
    def __init__(self, fogbow_ip, as_port):
        self.as_url = "http://%s:%s" % (fogbow_ip, as_port)

    def get_token(self, user_public_key, username, password, federation):
        token_endpoint = self.as_url + "/as/tokens"
        
        headers = {
            "Content-Type": "application/json"
        }

        body = {"publicKey": user_public_key, 
            "credentials": {
                "username":username,
                "password":password,
                "federation":federation
            }
        }

        token_response = requests.request("POST", token_endpoint, headers=headers, data=json.dumps(body))
        return token_response.json()["token"]

class Federation_Admin:
    def __init__(self, admin_name, admin_email, admin_description, admin_enabled):
        self.name = admin_name
        self.email = admin_email
        self.description = admin_description
        self.enabled = admin_enabled
        
class Federation:
    def __init__(self, name, description, enabled):
        self.name = name
        self.description = description
        self.enabled = enabled

class Federation_Service:
    def __init__(self, owner, endpoint, metadata, discovery_policy, access_policy):
        self.owner = owner
        self.endpoint = endpoint
        self.metadata = metadata
        self.discovery_policy = discovery_policy
        self.access_policy = access_policy
    
class FHS_Client:
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
        
        add_new_fed_admin_response = requests.request("POST", add_new_fed_admin_endpoint, headers=headers, data=json.dumps(body))
        
        return add_new_fed_admin_response.json()["memberId"]
    
    def create_federation(self, token, name, description, enabled):
        create_federation_endpoint = self.fhs_url + "/fhs/Federation"
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "name": name,
            "description": description, 
            "enabled": enabled
        }
        
        create_federation_response = requests.request("POST", create_federation_endpoint, headers=headers, data=json.dumps(body))
        
        return create_federation_response.json()["id"]
    
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
        
        grant_membership_response = requests.request("POST", grant_membership_endpoint, headers=headers, data=json.dumps(body))
        
        return grant_membership_response.json()
    
    def register_service(self, token, federation_id, owner_id, endpoint, metadata, discovery_policy, access_policy):
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
        
        register_service_response = requests.request("POST", register_service_endpoint, headers=headers, data=json.dumps(body))
        
        return register_service_response.json()["serviceId"]
    
    def invoke_service(self, token, federation_id, service_id, method, invocation_path, invocation_headers, invocation_body):
        invoke_service_endpoint = self.fhs_url + "/fhs/Invocation/" + federation_id + "/" + service_id
        
        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }
        
        body = {
            "path": invocation_path,
            "headers": invocation_headers,
            "body": invocation_body
        }
        
        invoke_service_response = requests.request(method, invoke_service_endpoint, headers=headers, data=json.dumps(body))
        
        return invoke_service_response.content

class TestUtils_Client:
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
        
        rewrap_response = requests.request("GET", rewrap_endpoint, headers=headers, data=json.dumps(body))
        return rewrap_response.content.decode("utf-8")

class Test1:
    
    def run(self, as_client, fhs_client, test_utils_client, configuration):
        federation_admin = configuration.load_federation_admin("admin")
        federation = configuration.load_federation("federation")
        federation_service = configuration.load_service("service")
        
        print("### Getting token")
        user_token = as_client.get_token(configuration.user_public_key, configuration.username, configuration.password, "")
        print("Token: %s" % (user_token,))
    
        print("### Getting fhs public key") 
        fhs_public_key = fhs_client.get_public_key()
        print("FHS Public key: %s" % (fhs_public_key,))
    
        print("### Rewrapping token")
        no_federation_fhs_token = test_utils_client.rewrap(user_token, fhs_public_key)
        print("Token: %s" % (no_federation_fhs_token,))
    
        print("### Adding new fed admin")
        response = fhs_client.add_new_fed_admin(no_federation_fhs_token, federation_admin.name, federation_admin.email, federation_admin.description, federation_admin.enabled)
        print("Response: %s" % (str(response),))
    
        print("### Creating federation")
        federation_id = fhs_client.create_federation(no_federation_fhs_token, federation.name, federation.description, federation.enabled)
        print("Federation id: %s" % (federation_id,))
        
        print("### Granting membership")
        response = fhs_client.grant_membership(no_federation_fhs_token, federation_id, federation_admin.name, federation_admin.email, federation_admin.description, federation_admin.enabled)
        print("Member id: %s" % (str(response),))
        
        print("### Registering service")
        service_id = fhs_client.register_service(no_federation_fhs_token, federation_id, federation_service.owner, federation_service.endpoint, 
                                                 federation_service.metadata, federation_service.discovery_policy, federation_service.access_policy)
        print("Service id: %s" % (service_id,))
        
        print("### Invoking service")
        response = fhs_client.invoke_service(no_federation_fhs_token, federation_id, service_id, "GET", [], {"Content-Type":"application/json", "Fogbow-User-Token":no_federation_fhs_token}, {})
        print("Response: %s" % (str(response),))
        

class Test_Runner:
    def __init__(self):
        configuration = Configuration_Loader("fhs_test.conf")
    
        as_client = AS_Client(configuration.fogbow_ip, configuration.as_port)
        fhs_client = FHS_Client(configuration.fogbow_ip, configuration.fhs_port)
        test_utils_client = TestUtils_Client(configuration.fogbow_ip, configuration.test_utils_port)

        Test1().run(as_client, fhs_client, test_utils_client, configuration)

if __name__ == "__main__":
    Test_Runner()
    
