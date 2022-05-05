import json
import requests


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
