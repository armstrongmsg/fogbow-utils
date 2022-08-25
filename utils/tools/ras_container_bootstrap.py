import os

from utils.tools.shell import ShellCommandBuilder
from utils.tools.shell import CreateDirectory
from utils.tools.shell import CopyDirectory
from utils.tools.shell import CopyFile
from utils.tools.logger import Log
from utils.tools.docker_utils import stop_container
from utils.tools.docker_utils import remove_container
from utils.tools.docker_utils import list_images_with_name
from utils.clients.ras_client import RASClient


LOGGER = Log("TestLog", "test.log")


class RasContainerBootstrap:
    def __init__(self, as_build_path, ms_build_path, ras_port, ras_config,
                 ras_src_path, ras_bootstrap_workspace):
        self.as_build_path = as_build_path
        self.ms_build_path = ms_build_path
        self.ras_port = ras_port
        self.ras_config = ras_config
        self.ras_container_name = "fogbow-ras-" + ras_config
        self.ras_src_path = ras_src_path
        self.ras_bootstrap_workspace = ras_bootstrap_workspace
        self.dependencies_path = ras_bootstrap_workspace + "/dependencies"
        self.conf_file_path = ras_bootstrap_workspace + "/conf-files"

    def prepare_code(self):
        LOGGER.log("Copying RAS code")
        CopyDirectory(self.ras_src_path, self.ras_bootstrap_workspace).run().wait()

    def prepare_dependencies(self):
        LOGGER.log("Copying AS build path")
        CopyDirectory(self.as_build_path, self.dependencies_path).run().wait()
        LOGGER.log("Copying MS build path")
        CopyDirectory(self.ms_build_path, self.dependencies_path).run().wait()
        LOGGER.log("Copying build and run scripts")
        CopyFile(os.getcwd() + "/test_build/ras/build.sh", self.ras_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/ras/build_base.sh", self.ras_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/ras/run.sh", self.ras_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/ras/Dockerfile", self.ras_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/ras/Dockerfile_base", self.ras_bootstrap_workspace).run().wait()

    def build(self):
        LOGGER.log("Building RAS %s" % self.ras_config)
        print(self.ras_bootstrap_workspace)

        if not len(list_images_with_name("fogbow/resource-allocation-service:base")) > 0:
            ShellCommandBuilder("bash"). \
                with_arg("build_base.sh"). \
                in_directory(self.ras_bootstrap_workspace). \
                build().run().wait()

        ShellCommandBuilder("bash").\
            with_arg("build.sh").\
            in_directory(self.ras_bootstrap_workspace).\
            build().run().wait()

    def prepare_config(self):
        LOGGER.log("Copying conf files")
        CreateDirectory(self.conf_file_path).run().wait()
        CopyFile(os.getcwd() + "/test_configs/" + self.ras_config + "/application.properties", self.conf_file_path).run().wait()
        CopyDirectory(os.getcwd() + "/test_configs/" + self.ras_config + "/private", self.conf_file_path).run().wait()

    def start(self):
        LOGGER.log("Starting RAS %s" % self.ras_config)
        ShellCommandBuilder("bash").\
            with_arg("run.sh").\
            with_arg(self.ras_bootstrap_workspace).\
            with_arg(self.ras_container_name).\
            with_arg(self.ras_port).\
            in_directory(self.ras_bootstrap_workspace).\
            build().run().wait()

        LOGGER.log("Waiting until RAS is ready.")
        ras_client = RASClient("0.0.0.0", int(self.ras_port))

        ras_client.wait_until_is_active()
        LOGGER.log("RAS is ready")

    def deploy(self):
        self.prepare_code()
        self.prepare_dependencies()
        self.build()
        self.prepare_config()
        self.start()

    def cleanup(self):
        LOGGER.log("Stopping and removing RAS %s" % self.ras_config)
        stop_container(self.ras_container_name)
        remove_container(self.ras_container_name)
