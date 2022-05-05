import subprocess
import time

from pathlib import Path


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
            self.process = subprocess.Popen(
                args=[self.as_env_path + "authentication-service/mvnw", "spring-boot:run"], shell=False,
                env=self.env_var, cwd=self.as_env_path + "authentication-service", stdout=f, stderr=f)

    def stop_as(self):
        subprocess.run(args=["kill", str(self.process.pid)])
