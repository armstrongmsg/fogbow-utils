import configparser
import time

import fogbow_client
import fogbow_tools

from shutil import copy2


class TestRunner:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.conf")

        self.ras_project_base_path = config.get("configuration", "ras_project_base_path")
        self.as_project_base_path = config.get("configuration", "as_project_base_path")
        self.base_conf = config.get("configuration", "base_conf")
        self.modified_conf = config.get("configuration", "modified_conf")
        self.public_key = config.get("configuration", "public_key")
        self.username = config.get("configuration", "username")
        self.password = config.get("configuration", "password")
        self.java_home = config.get("configuration", "java_home")
        self.RAS_host = config.get("configuration", "RAS_host")
        self.RAS_port = int(config.get("configuration", "RAS_port"))
        self.AS_host = config.get("configuration", "AS_host")
        self.AS_port = int(config.get("configuration", "AS_port"))

        self.auth_service = None
        self.ra_service = None
        self.token = None
        self.rasc = None

    def _start_up(self):
        print("Starting AS")
        self.auth_service = fogbow_tools.ASBootstrap(self.as_project_base_path, self.java_home)
        self.auth_service.start_as()
        time.sleep(20)

        print("Starting RAS")
        self.ra_service = fogbow_tools.RASBootstrap(self.ras_project_base_path, self.java_home)
        self.ra_service.start_ras()
        time.sleep(20)

        asc = fogbow_client.ASClient(self.AS_host, self.AS_port)
        self.token = asc.tokens(self.public_key, self.username, self.password)

        self.rasc = fogbow_client.RASClient(self.RAS_host, self.RAS_port)
        print(self.rasc.clouds(self.token))

    def _change_config(self):
        print("Updating configuration file")

        copy2(self.ras_project_base_path + self.modified_conf, self.ras_project_base_path +
              "/target/classes/private/ras.conf")

        time.sleep(10)

        print("Reloading RAS configuration")
        self.rasc.reload(self.token)
        time.sleep(10)

    def _check(self):
        print("Checking clouds names")
        print(self.rasc.clouds(self.token))

    def _cleanup(self):
        copy2(self.ras_project_base_path + self.base_conf, self.ras_project_base_path +
              "/target/classes/private/ras.conf")

        self.auth_service.stop_as()
        self.ra_service.stop_ras()

    def run(self):
        self._start_up()
        self._change_config()
        self._check()
        self._cleanup()


if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
