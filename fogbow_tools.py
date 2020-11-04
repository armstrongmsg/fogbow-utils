import subprocess
import time

from shutil import copy2
from pathlib import Path


class RASBootstrap:
    def __init__(self, base_conf, ras_project_base_path, ras_env_path, java_home):
        self.base_conf = base_conf
        self.ras_project_base_path = ras_project_base_path
        self.ras_env_path = ras_env_path
        self.env_var = {"JAVA_HOME": java_home}
        self.process = None

    def start_ras(self):
        p = Path(self.ras_env_path + "resource-allocation-service")

        if not p.exists():
            subprocess.Popen(args=["cp", "-r", self.ras_project_base_path, self.ras_env_path])
            time.sleep(10)

        copy2(self.base_conf, self.ras_env_path +
              "resource-allocation-service/target/classes/private/ras.conf")

        with open("ras.log", "w") as f:
            self.process = subprocess.Popen(args=[self.ras_env_path + "resource-allocation-service/mvnw",
                                                  "spring-boot:run"], cwd=self.ras_env_path + "resource-allocation-service",
                                            shell=False, env=self.env_var,
                                            stdout=f, stderr=f)

    def stop_ras(self):
        subprocess.run(args=["kill", str(self.process.pid)])


class ASBootstrap:
    def __init__(self, as_project_base_path, as_env_path, java_home):
        self.as_project_base_path = as_project_base_path
        self.as_env_path = as_env_path
        self.env_var = {"JAVA_HOME": java_home}
        self.process = None

    def start_as(self):
        p = Path(self.as_env_path + "authentication-service")

        if not p.exists():
            subprocess.Popen(args=["cp", "-r", self.as_project_base_path, self.as_env_path])
            time.sleep(5)

        with open("as.log", "w") as f:
            self.process = subprocess.Popen(args=[self.as_env_path + "authentication-service/mvnw", "spring-boot:run"],
                                            shell=False, env=self.env_var, cwd=self.as_env_path + "authentication-service",
                                            stdout=f, stderr=f)

    def stop_as(self):
        subprocess.run(args=["kill", str(self.process.pid)])
