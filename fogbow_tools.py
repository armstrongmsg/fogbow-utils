import subprocess


class RASBootstrap:
    def __init__(self, ras_project_base_path, java_home):
        self.ras_project_base_path = ras_project_base_path
        self.env_var = {"JAVA_HOME": java_home}
        self.process = None

    def start_ras(self):
        with open("ras.log", "w") as f:
            self.process = subprocess.Popen(args=[self.ras_project_base_path + "/mvnw", "spring-boot:run"],
                                            shell=False, env=self.env_var, cwd=self.ras_project_base_path,
                                            stdout=f, stderr=f)

    def stop_ras(self):
        subprocess.run(args=["kill", str(self.process.pid)])


class ASBootstrap:
    def __init__(self, as_project_base_path, java_home):
        self.as_project_base_path = as_project_base_path
        self.env_var = {"JAVA_HOME": java_home}
        self.process = None

    def start_as(self):
        with open("as.log", "w") as f:
            self.process = subprocess.Popen(args=[self.as_project_base_path + "/mvnw", "spring-boot:run"],
                                            shell=False, env=self.env_var, cwd=self.as_project_base_path,
                                            stdout=f, stderr=f)

    def stop_as(self):
        subprocess.run(args=["kill", str(self.process.pid)])
