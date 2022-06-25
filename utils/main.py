from utils.runner import *
from utils.tools import logger


def main():
    logger.configure_logging()
    logger.enable()

    TestRunner()
