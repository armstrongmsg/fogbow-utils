import configparser
import json


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
        self.test_classes = self.config["conf"]["test_classes"].split(",")

    def load_federation_admin(self, admin_name):
        admin_username = self.config[admin_name]["username"]
        admin_password = self.config[admin_name]["password"]
        admin_email = self.config[admin_name]["email"]
        admin_description = self.config[admin_name]["description"]

        if self.config[admin_name]["enabled"] == "True":
            admin_enabled = True
        else:
            admin_enabled = False

        return FederationAdmin(admin_username, admin_password, admin_email,
                               admin_description, admin_enabled)

    def load_user(self, user_name):
        user_username = self.config[user_name]["username"]
        user_password = self.config[user_name]["password"]

        user_authentication_class_name = self.config[user_name]["authentication_class_name"]
        user_authentication_properties = {
            "identityPluginClassName": user_authentication_class_name
        }

        user_email = self.config[user_name]["email"]
        user_description = self.config[user_name]["description"]

        if self.config[user_name]["enabled"] == "True":
            user_enabled = True
        else:
            user_enabled = False

        return FederationUser(user_username, user_password, user_authentication_properties,
                              user_email, user_description, user_enabled)

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
        service_invoker_class_name = self.config[service_name]["invoker"]
        service_access_policy_rules_file_name = self.config[service_name]["access_rules_file_name"]

        with open(service_access_policy_rules_file_name) as service_access_policy_rules_file:
            service_access_policy_rules = "".join(service_access_policy_rules_file.readlines())

        service_public_key_endpoint = self.config[service_name]["service_public_key_endpoint"]

        service_metadata = {
            "servicePublicKeyEndpoint": service_public_key_endpoint,
            "invokerClassName": service_invoker_class_name,
            "accessPolicyRules": service_access_policy_rules
        }
        service_discovery_policy = self.config[service_name]["discovery_policy"]
        service_access_policy = self.config[service_name]["access_policy"]

        return FederationService(service_owner, service_endpoint, service_metadata,
                                 service_discovery_policy, service_access_policy)


class FederationAdmin:
    def __init__(self, admin_name, admin_password, admin_email, admin_description, admin_enabled):
        self.name = admin_name
        self.password = admin_password
        self.email = admin_email
        self.description = admin_description
        self.enabled = admin_enabled


class FederationUser:
    def __init__(self, admin_name, admin_password, authentication_properties, admin_email,
                 admin_description, admin_enabled):
        self.name = admin_name
        self.password = admin_password
        self.authentication_properties = authentication_properties
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
