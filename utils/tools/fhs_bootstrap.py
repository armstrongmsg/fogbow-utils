import time
import os
import requests

from utils.tools.shell import ShellCommandBuilder
from utils.tools.shell import CopyDirectory
from utils.tools.shell import CopyFile
from utils.tools.shell import CreateDirectory
from utils.tools.logger import Log
from utils.tools.docker_utils import stop_container
from utils.tools.docker_utils import remove_container
from utils.tools.docker_utils import list_images_with_name
from utils.clients.fhs_client import FHSClient


LOGGER = Log("TestLog", "test.log")


class FHSBootstrap:
    def __init__(self, as_build_path, ras_build_path, ms_build_path, fhs_port, fhs_config,
                 fhs_src_path, fhs_bootstrap_workspace):
        self.as_build_path = as_build_path
        self.ras_build_path = ras_build_path
        self.ms_build_path = ms_build_path
        self.fhs_port = fhs_port
        self.fhs_config = fhs_config
        self.fhs_container_name = "fogbow-fhs-" + fhs_config
        self.fhs_src_path = fhs_src_path
        self.fhs_bootstrap_workspace = fhs_bootstrap_workspace
        self.dependencies_path = fhs_bootstrap_workspace + "/dependencies"
        self.conf_file_path = fhs_bootstrap_workspace + "/conf-files"

    def prepare_code(self):
        LOGGER.log("Copying FHS code")
        CopyDirectory(self.fhs_src_path, self.fhs_bootstrap_workspace).run().wait()

    def prepare_dependencies(self):
        LOGGER.log("Copying AS build path")
        CopyDirectory(self.as_build_path, self.dependencies_path).run().wait()
        LOGGER.log("Copying RAS build path")
        CopyDirectory(self.ras_build_path, self.dependencies_path).run().wait()
        LOGGER.log("Copying MS build path")
        CopyDirectory(self.ms_build_path, self.dependencies_path).run().wait()
        LOGGER.log("Copying build and run scripts")
        CopyFile(os.getcwd() + "/test_build/fhs/build.sh", self.fhs_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/fhs/build_base.sh", self.fhs_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/fhs/run.sh", self.fhs_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/fhs/Dockerfile", self.fhs_bootstrap_workspace).run().wait()
        CopyFile(os.getcwd() + "/test_build/fhs/Dockerfile_base", self.fhs_bootstrap_workspace).run().wait()

    def build(self):
        LOGGER.log("Building FHS %s" % self.fhs_config)
        print(self.fhs_bootstrap_workspace)

        if not len(list_images_with_name("fogbow/federation-hosting-service:base")) > 0:
            ShellCommandBuilder("bash"). \
                with_arg("build_base.sh"). \
                in_directory(self.fhs_bootstrap_workspace). \
                build().run().wait()

        ShellCommandBuilder("bash").\
            with_arg("build.sh").\
            in_directory(self.fhs_bootstrap_workspace).\
            build().run().wait()

    def prepare_config(self):
        LOGGER.log("Copying conf files")
        CreateDirectory(self.conf_file_path).run().wait()
        CopyFile(os.getcwd() + "/test_configs/" + self.fhs_config + "/application.properties", self.conf_file_path).run().wait()
        CopyDirectory(os.getcwd() + "/test_configs/" + self.fhs_config + "/private", self.conf_file_path).run().wait()

    def start(self):
        LOGGER.log("Starting FHS %s" % self.fhs_config)
        ShellCommandBuilder("bash").\
            with_arg("run.sh").\
            with_arg(self.fhs_bootstrap_workspace).\
            with_arg(self.fhs_container_name).\
            with_arg(self.fhs_port).\
            in_directory(self.fhs_bootstrap_workspace).\
            build().run().wait()

        LOGGER.log("Waiting until FHS is ready.")
        fhs_client = FHSClient("0.0.0.0", self.fhs_port)

        while True:
            try:
                fhs_client.get_public_key()
                break
            except requests.exceptions.ConnectionError as e:
                time.sleep(5)
            except KeyError as e:
                time.sleep(5)

        LOGGER.log("FHS is ready")

    def deploy(self):
        self.prepare_code()
        self.prepare_dependencies()
        self.build()
        self.prepare_config()
        self.start()

    def cleanup(self):
        LOGGER.log("Stopping and removing FHS %s" % self.fhs_config)
        stop_container(self.fhs_container_name)
        remove_container(self.fhs_container_name)
