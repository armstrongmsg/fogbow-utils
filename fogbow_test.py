import configparser
import time

import fogbow_client
import fogbow_tools

from shutil import copy2


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.conf")

    ras_project_base_path = config.get("configuration", "ras_project_base_path")
    as_project_base_path = config.get("configuration", "as_project_base_path")
    base_conf = config.get("configuration", "base_conf")
    modified_conf = config.get("configuration", "modified_conf")
    publicKey = config.get("configuration", "public_key")
    username = config.get("configuration", "username")
    password = config.get("configuration", "password")
    java_home = config.get("configuration", "java_home")
    RAS_host = config.get("configuration", "RAS_host")
    RAS_port = int(config.get("configuration", "RAS_port"))
    AS_host = config.get("configuration", "AS_host")
    AS_port = int(config.get("configuration", "AS_port"))

    print("Starting AS")
    print("---------------------------------")
    print("---------------------------------")
    auth_service = fogbow_tools.ASBootstrap(as_project_base_path, java_home)
    auth_service.start_as()
    time.sleep(20)

    print("Starting RAS")
    print("---------------------------------")
    print("---------------------------------")
    ra_service = fogbow_tools.RASBootstrap(ras_project_base_path, java_home)
    ra_service.start_ras()
    time.sleep(20)

    asc = fogbow_client.ASClient(AS_host, AS_port)
    token = asc.tokens(publicKey, username, password)

    rasc = fogbow_client.RASClient(RAS_host, RAS_port)
    print(rasc.clouds(token))

    print("Updating configuration file")
    print("---------------------------------")
    print("---------------------------------")

    copy2(ras_project_base_path + modified_conf, ras_project_base_path + "/target/classes/private/ras.conf")

    time.sleep(30)

    print("Reloading RAS configuration")
    print("---------------------------------")
    print("---------------------------------")
    rasc.reload(token)
    time.sleep(30)

    print("Checking clouds names")
    print("---------------------------------")
    print("---------------------------------")
    print(rasc.clouds(token))

    copy2(ras_project_base_path + base_conf, ras_project_base_path + "/target/classes/private/ras.conf")

    auth_service.stop_as()
    ra_service.stop_ras()
