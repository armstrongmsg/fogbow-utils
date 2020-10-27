import configparser


class RASConf:
    def __init__(self, project_base_path):
        self.project_base_path = project_base_path
        self.config = configparser.RawConfigParser()

        with open(self.project_base_path + "/src/main/resources/private/ras.conf") as f:
            file_content = '[dummy_section]\n' + f.read()
        self.config.read_string(file_content)

    def get_property(self, property_name):
        return self.config["dummy_section"][property_name]