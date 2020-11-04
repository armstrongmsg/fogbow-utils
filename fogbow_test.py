import configparser

import fogbow_client
import fogbow_tools
import fogbow_utils

from shutil import copy2

from tests import CloudsTest, NetworksTest


class TestRunner:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.conf")

        self.ras_project_base_path = config.get("configuration", "ras_project_base_path")
        self.as_project_base_path = config.get("configuration", "as_project_base_path")
        # TODO improve this
        self.project_path = config.get("configuration", "project_path")
        self.ras_env_path = self.project_path + "/env/ras/"
        self.as_env_path = self.project_path + "/env/as/"
        self.project_ras_conf_location = "resource-allocation-service/target/classes/private/ras.conf"
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
        self.auth_service = fogbow_tools.ASBootstrap(self.as_project_base_path, self.as_env_path, self.java_home)
        self.auth_service.start_as()

        asc = fogbow_client.ASClient(self.AS_host, self.AS_port)
        asc.wait_until_is_active()
        print("Getting token")
        self.token = asc.tokens(self.public_key, self.username, self.password)

        print("Starting RAS")
        self.ra_service = fogbow_tools.RASBootstrap(self.base_conf, self.ras_project_base_path, self.ras_env_path,
                                                    self.java_home)
        self.ra_service.start_ras()

        self.rasc = fogbow_client.RASClient(self.RAS_host, self.RAS_port)
        self.rasc.wait_until_is_active()
        print(self.rasc.clouds(self.token))

    def _change_config(self):
        print("Updating configuration file")

        copy2(self.modified_conf, self.ras_env_path +
              self.project_ras_conf_location)

        print("Reloading RAS configuration")
        self.rasc.reload(self.token)

    def _check(self):
        config = fogbow_utils.RASConf(self.modified_conf)
        cloud_names = config.get_property("cloud_names")
        cloud_test = CloudsTest(self.rasc, self.token, cloud_names)

        networks_test = NetworksTest(ras_client=self.rasc, token=self.token)

        test_list = []

        test_list.append(cloud_test)
        test_list.append(networks_test)

        for test in test_list:
            try:
                test_result = test.test()

                if test_result:
                    result = "OK"
                else:
                    result = "Failed"

                print("{}: {}".format(test.get_test_name(), result))
            except:
                print("{}: Error".format(test.get_test_name()))
            finally:
                test.cleanup()

    def _cleanup(self):
        copy2(self.base_conf, self.ras_env_path +
              self.project_ras_conf_location)

        if self.auth_service is not None:
            self.auth_service.stop_as()

        if self.ra_service is not None:
            self.ra_service.stop_ras()

    def run(self):
        try:
            self._start_up()
            self._change_config()
            self._check()
        finally:
            self._cleanup()


if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
