import io
import subprocess
import sys


class ShellCommandBuilder:
    def __init__(self, command):
        self.args = [command]
        self.env = {}
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.cwd = "/"

    def with_arg(self, command_arg):
        self.args.append(command_arg)
        return self

    def with_env_var(self, var_name, var_value):
        self.env[var_name] = var_value
        return self

    def with_stdout(self, stdout):
        self.stdout = stdout
        return self

    def with_stderr(self, stderr):
        self.stderr = stderr
        return self

    def in_directory(self, cwd):
        self.cwd = cwd
        return self

    def build(self):
        return ShellCommand(self.env, self.cwd, self.stdout, self.stderr, self.args)


class ShellCommand:
    def __init__(self, env, cwd, stdout, stderr, args):
        self.env = env
        self.cwd = cwd
        self.stdout = stdout
        self.stderr = stderr
        self.args = args
        self.process = None

    def run(self):
        self.process = subprocess.Popen(args=self.args, shell=False,
                                        env=self.env, cwd=self.cwd,
                                        stdout=self.stdout, stderr=self.stderr)
        return self

    def wait(self):
        self.process.wait()

    def read_output(self):
        output = []
        for line in io.TextIOWrapper(self.process.stdout, encoding="utf-8"):
            output.append(line)
        return output

    def kill(self):
        subprocess.run(args=["kill", str(self.process.pid)])


class CopyFile(ShellCommand):
    def __init__(self, src, dest):
        super().__init__(env={}, cwd="/", stdout=sys.stdout,
                         stderr=sys.stderr, args=["cp", src, dest])


class CopyDirectory(ShellCommand):
    def __init__(self, src, dest):
        super().__init__(env={}, cwd="/", stdout=sys.stdout,
                         stderr=sys.stderr, args=["cp", "-r", src, dest])
