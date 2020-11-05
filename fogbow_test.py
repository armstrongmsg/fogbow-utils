import configparser

import fogbow_client
import fogbow_tools

from shutil import copy2

from tests import CloudsTest, NetworksTest, CloudsTestBeforeReload


class TestRunner:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.conf")

        self.ras_project_base_path = config.get("configuration", "ras_project_base_path")
        self.as_project_base_path = config.get("configuration", "as_project_base_path")
        # TODO improve this
        self.project_path = config.get("configuration", "project_path")
        self.ras_env_path_1 = self.project_path + "/env/ras1/"
        self.ras_env_path_2 = self.project_path + "/env/ras2/"
        self.as_env_path = self.project_path + "/env/as/"
        self.project_ras_conf_location = "resource-allocation-service/target/classes/private/ras.conf"
        self.base_conf_ras_1 = config.get("configuration", "base_conf_ras_1")
        self.modified_conf_ras_1 = config.get("configuration", "modified_conf_ras_1")
        self.base_conf_ras_2 = config.get("configuration", "base_conf_ras_2")
        self.modified_conf_ras_2 = config.get("configuration", "modified_conf_ras_2")
        self.application_properties_ras_1 = config.get("configuration", "application_properties_ras_1")
        self.application_properties_ras_2 = config.get("configuration", "application_properties_ras_2")
        self.public_key = config.get("configuration", "public_key")
        self.username = config.get("configuration", "username")
        self.password = config.get("configuration", "password")
        self.java_home = config.get("configuration", "java_home")
        self.RAS_host_1 = config.get("configuration", "RAS_host_1")
        self.RAS_port_1 = int(config.get("configuration", "RAS_port_1"))
        self.RAS_host_2 = config.get("configuration", "RAS_host_2")
        self.RAS_port_2 = int(config.get("configuration", "RAS_port_2"))
        self.AS_host = config.get("configuration", "AS_host")
        self.AS_port = int(config.get("configuration", "AS_port"))

        self.auth_service = None
        self.ra_service = None
        self.ra_service_2 = None
        self.token = None
        self.rasc_1 = None

    def _start_up(self):
        print("Starting AS")
        self.auth_service = fogbow_tools.ASBootstrap(self.as_project_base_path, self.as_env_path, self.java_home)
        self.auth_service.start_as()

        asc = fogbow_client.ASClient(self.AS_host, self.AS_port)
        asc.wait_until_is_active()
        print("Getting token")
        self.token = asc.tokens(self.public_key, self.username, self.password)

        print("Starting RAS 1")
        self.ra_service = fogbow_tools.RASBootstrap(self.base_conf_ras_1, self.ras_project_base_path, self.ras_env_path_1,
                                                    self.java_home, self.application_properties_ras_1)
        self.ra_service.start_ras()

        self.rasc_1 = fogbow_client.RASClient(self.RAS_host_1, self.RAS_port_1)
        self.rasc_1.wait_until_is_active()

        print("Starting RAS 2")
        self.ra_service_2 = fogbow_tools.RASBootstrap(self.base_conf_ras_2, self.ras_project_base_path, self.ras_env_path_2,
                                                      self.java_home, self.application_properties_ras_2)
        self.ra_service_2.start_ras()

        self.rasc_2 = fogbow_client.RASClient(self.RAS_host_2, self.RAS_port_2)
        self.rasc_2.wait_until_is_active()

        print(self.rasc_1.clouds(self.token))
        print(self.rasc_2.clouds(self.token))

    def _change_config(self):
        print("Updating configuration file")

        copy2(self.modified_conf_ras_1, self.ras_env_path_1 +
              self.project_ras_conf_location)

        copy2(self.modified_conf_ras_2, self.ras_env_path_2 +
              self.project_ras_conf_location)

        print("Reloading RAS configuration")
        self.rasc_1.reload(self.token)
        self.rasc_2.reload(self.token)

    def _check_pre_reload(self):
        print("Check pre reload")
        cloud_test = CloudsTestBeforeReload(self.rasc_1, self.rasc_2, self.token)

        test_list = []

        test_list.append(cloud_test)

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

    def _check(self):
        cloud_test = CloudsTest(self.rasc_1, self.rasc_2, self.token)
        networks_test = NetworksTest(ras_client=self.rasc_1, token=self.token)

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
        copy2(self.base_conf_ras_1, self.ras_env_path_1 +
              self.project_ras_conf_location)

        copy2(self.base_conf_ras_2, self.ras_env_path_2 +
              self.project_ras_conf_location)

        if self.auth_service is not None:
            self.auth_service.stop_as()

        if self.ra_service is not None:
            self.ra_service.stop_ras()

        if self.ra_service_2 is not None:
            self.ra_service_2.stop_ras()

    def run(self):
        try:
            self._start_up()
            self._check_pre_reload()
            self._change_config()
            self._check()
        finally:
            self._cleanup()


if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
