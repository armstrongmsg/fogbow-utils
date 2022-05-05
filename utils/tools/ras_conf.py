import configparser


class RASConf:
    def __init__(self, config_file):
        self.config = configparser.RawConfigParser()

        with open(config_file) as f:
            file_content = '[dummy_section]\n' + f.read()
        self.config.read_string(file_content)

    def get_property(self, property_name):
        return self.config["dummy_section"][property_name]
