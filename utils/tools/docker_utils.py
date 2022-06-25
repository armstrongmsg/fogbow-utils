import subprocess

from utils.tools.shell import ShellCommandBuilder


def stop_container(container_name):
    ShellCommandBuilder("docker"). \
        with_arg("stop"). \
        with_arg(container_name). \
        build().run().wait()


def remove_container(container_name):
    ShellCommandBuilder("docker"). \
        with_arg("rm"). \
        with_arg(container_name). \
        build().run().wait()


def list_images_with_name(image_name):
    return ShellCommandBuilder("docker"). \
        with_arg("images"). \
        with_arg(image_name). \
        with_arg("--format").with_arg("\"{{.ID}}\""). \
        with_stdout(subprocess.PIPE). \
        build().run().read_output()
