import json
import requests


class FHSClient:
    def __init__(self, fogbow_ip, fhs_port):
        self.fhs_url = "http://%s:%s" % (fogbow_ip, fhs_port)

    def get_public_key(self):
        public_key_endpoint = self.fhs_url + "/fhs/publicKey"
        public_key_response = requests.request("GET", public_key_endpoint)
        return public_key_response.json()["publicKey"]

    def reload(self, token):
        reload_endpoint = self.fhs_url + "/fhs/FHSOperator/reload"

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        reload_response = requests.request("POST", reload_endpoint, headers=headers,
                                           data=json.dumps(body))

        return reload_response

    def add_new_fed_admin(self, token, name, email, description, enabled, authentication_properties):
        add_new_fed_admin_endpoint = self.fhs_url + "/fhs/FHSOperator/NewFedAdmin"

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "name": name,
            "email": email,
            "description": description,
            "enabled": enabled,
            "authenticationProperties": authentication_properties
        }

        add_new_fed_admin_response = requests.request("POST", add_new_fed_admin_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return add_new_fed_admin_response.json()["memberId"]

    def list_fed_admins(self, token):
        list_fed_admins_endpoint = self.fhs_url + "/fhs/FHSOperator/FedAdmins"

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        list_fed_admins_response = requests.request("GET", list_fed_admins_endpoint,
                                                    headers=headers, data=json.dumps(body))

        return list_fed_admins_response.json()

    def update_fed_admin(self, token, member_id, member_name, email, description, enabled):
        update_fed_admin_endpoint = self.fhs_url + "/fhs/FHSOperator/FedAdmin/" + member_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "memberName": member_name,
            "email": email,
            "description": description,
            "enabled": enabled
        }

        update_fed_admin_response = requests.request("PUT", update_fed_admin_endpoint,
                                                     headers=headers, data=json.dumps(body))

        return update_fed_admin_response.status_code

    def delete_fed_admin(self, token, member_id):
        delete_fed_admin_endpoint = self.fhs_url + "/fhs/FHSOperator/FedAdmin/" + member_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        delete_fed_admin_response = requests.request("DELETE", delete_fed_admin_endpoint,
                                                     headers=headers, data=json.dumps(body))

        return delete_fed_admin_response.status_code

    def list_federation_instances(self, token):
        list_federation_instances_endpoint = self.fhs_url + "/fhs/FHSOperator/FedInstances"

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        list_federation_instances_response = requests.request("GET", list_federation_instances_endpoint,
                                                              headers=headers, data=json.dumps(body))

        return list_federation_instances_response.json()

    def update_federation(self, token, federation_id, enabled):
        update_federation_endpoint = self.fhs_url + "/fhs/FHSOperator/FedInstance/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "enabled": enabled
        }

        update_federation_response = requests.request("PUT", update_federation_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return update_federation_response.json()

    def delete_federation_instance(self, token, federation_id):
        delete_federation_endpoint = self.fhs_url + "/fhs/FHSOperator/FedInstance/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        delete_federation_response = requests.request("PUT", delete_federation_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return delete_federation_response.json()

    #
    #
    # Federation
    #
    #

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

    def get_federations(self, token, federation_owner):
        get_federations_endpoint = self.fhs_url + "/fhs/Federation"

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "owner": federation_owner
        }

        get_federations_response = requests.request("GET", get_federations_endpoint,
                                                    headers=headers, data=json.dumps(body))

        return get_federations_response.json()

    def get_federation_info(self, token, federation_id, federation_owner):
        get_federation_info_endpoint = self.fhs_url + "/fhs/Federation/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "owner": federation_owner
        }

        get_federation_info_response = requests.request("GET", get_federation_info_endpoint,
                                                        headers=headers, data=json.dumps(body))

        return get_federation_info_response.json()

    def delete_federation(self, token, federation_id, federation_owner):
        delete_federation_endpoint = self.fhs_url + "/fhs/Federation/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "owner": federation_owner
        }

        delete_federation_response = requests.request("DELETE", delete_federation_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return delete_federation_response.status_code

    def get_remote_federation_list(self, token):
        get_remote_federation_list_endpoint = self.fhs_url + "/fhs/Federation/Query"

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        get_remote_federation_list_response = requests.request("GET", get_remote_federation_list_endpoint,
                                                               headers=headers, data=json.dumps(body))

        return get_remote_federation_list_response.json()

    #
    #
    # Attribute
    #
    #

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

    def delete_attribute(self, token, federation_id, attribute_id):
        delete_attribute_endpoint = self.fhs_url + "/fhs/Attributes/" + \
                                     federation_id + "/" + attribute_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        delete_attribute_response = requests.request("DELETE", delete_attribute_endpoint,
                                                     headers=headers, data=json.dumps(body))

        return delete_attribute_response.status_code

    #
    #
    # Membership
    #
    #

    def grant_membership(self, token, federation_id, username, authentication_properties, email, description, enabled):
        grant_membership_endpoint = self.fhs_url + "/fhs/Membership/" + federation_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "name": username,
            "authenticationProperties": authentication_properties,
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

    def revoke_membership(self, token, federation_id, member_id):
        revoke_membership_endpoint = self.fhs_url + "/fhs/Membership/" + \
                                     federation_id + "/" + member_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        revoke_membership_response = requests.request("DELETE", revoke_membership_endpoint,
                                                      headers=headers, data=json.dumps(body))

        return revoke_membership_response.status_code

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

    #
    #
    # Service
    #
    #

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

    def get_services(self, token, federation_id, owner_id):
        get_services_endpoint = self.fhs_url + "/fhs/Services/" + federation_id + "/" + owner_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        get_services_response = requests.request("GET", get_services_endpoint,
                                                 headers=headers, data=json.dumps(body))

        return get_services_response.json()

    def get_service(self, token, federation_id, owner_id, service_id):
        get_service_endpoint = self.fhs_url + "/fhs/Services/" + \
                               federation_id + "/" + owner_id + "/" + service_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        get_service_response = requests.request("GET", get_service_endpoint,
                                                headers=headers, data=json.dumps(body))

        return get_service_response.json()

    def update_service(self, token, federation_id, owner_id, service_id, metadata,
                       discovery_policy, access_policy):
        update_service_endpoint = self.fhs_url + "/fhs/Services/" + \
                               federation_id + "/" + owner_id + "/" + service_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {
            "metadata": metadata,
            "discoveryPolicy": discovery_policy,
            "accessPolicy": access_policy
        }

        update_service_response = requests.request("PUT", update_service_endpoint,
                                                   headers=headers, data=json.dumps(body))

        return update_service_response.status_code

    def delete_service(self, token, federation_id, owner_id, service_id):
        delete_service_endpoint = self.fhs_url + "/fhs/Services/" + \
                               federation_id + "/" + owner_id + "/" + service_id

        headers = {
            "Content-Type": "application/json",
            "Fogbow-User-Token": token
        }

        body = {}

        delete_service_response = requests.request("DELETE", delete_service_endpoint,
                                                   headers=headers, data=json.dumps(body))

        return delete_service_response.status_code

    #
    #
    # Invocation
    #
    #

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

    #
    #
    # Authentication
    #
    #

    def login(self, federation_id, member_id, credentials):
        login_endpoint = self.fhs_url + "/fhs/MemberLogin"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "federationId": federation_id,
            "memberId": member_id,
            "credentials": credentials
        }

        login_response = requests.request("POST", login_endpoint,
                                          headers=headers, data=json.dumps(body))

        return login_response.json()["token"]

    def login_operator(self, operator_id, credentials):
        login_operator_endpoint = self.fhs_url + "/fhs/FHSOperator/Login"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "operatorId": operator_id,
            "credentials": credentials
        }

        login_response = requests.request("POST", login_operator_endpoint,
                                          headers=headers, data=json.dumps(body))

        return login_response.json()["token"]

    def login_federation_admin(self, federation_admin_id, credentials):
        login_federation_admin_endpoint = self.fhs_url + "/fhs/MemberLogin/FedAdmin"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "federationAdminId": federation_admin_id,
            "credentials": credentials
        }

        login_response = requests.request("POST", login_federation_admin_endpoint,
                                          headers=headers, data=json.dumps(body))

        return login_response.json()["token"]
