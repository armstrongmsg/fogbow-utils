import logging
from datetime import datetime


global_enabled = False


class Log:
    def __init__(self, name, output_file_path):
        self.logger = logging.getLogger(name)
        if not len(self.logger.handlers):
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            handler = logging.FileHandler(output_file_path)
            self.logger.addHandler(handler)
            self.logger.propagate = False

    def log(self, text):
        if global_enabled:
            self.logger.info(text)


def enable():
    global global_enabled
    global_enabled = True


def disable():
    global global_enabled
    global_enabled = False


def configure_logging(logging_level="INFO"):
    levels = {"CRITICAL": logging.CRITICAL, "DEBUG": logging.DEBUG,
              "ERROR": logging.ERROR, "FATAL": logging.FATAL,
              "INFO": logging.INFO, "NOTSET": logging.NOTSET,
              "WARN": logging.WARN, "WARNING": logging.WARNING
              }

    logging.basicConfig(level=levels[logging_level])