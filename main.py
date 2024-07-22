import sys
import os
from os.path import join as path_join, exists
import importlib
from shlex import split as cmd_split
from enum import IntEnum, unique
from functools import cache
from subprocess import Popen

def execute(program, args):
    proc = Popen(args, executable=program,
                 stdin=sys.stdin,
                 stdout=sys.stdout,
                 stderr=sys.stderr)
    return proc.wait()

@cache
def cache_query(base):
    return query(base)

def query(base):
    for i in environ["PATH"].split(":"):
        try:
            listed = os.listdir(i)
        except FileNotFoundError:
            continue
        if base in listed:
            return ShellInfo.OK, path_join(i, base)
    return ShellInfo.CMD_NOT_FOUND, ""

@unique
class ShellInfo(IntEnum):
    OK = 0
    EXIT = -1
    CMD_NOT_FOUND = -2
    ERROR = -3

user_vars = {}
environ = os.environ
commands = importlib.import_module("builtin_fns")

cmds = {
    sym.replace("do_", "", 1) : getattr(commands, sym)
    for sym in dir(commands)
        if "do_" in sym
        and callable(getattr(commands, sym))
}

def write(*args, sep=" "):
    sys.stdout.write(sep.join(args))
    sys.stdout.flush()

def search(base: str, args: tuple[str, ...]):
    if not base:
        return ShellInfo.OK, ""
    if base in cmds:
        return ShellInfo.OK, cmds[base]

    status, cmd = query(base)

    if status == ShellInfo.CMD_NOT_FOUND:
        write(f"{base}: command not found\n")
        return ShellInfo.CMD_NOT_FOUND, ""
    return ShellInfo.OK, cmd

def common_routine(args):
    if not args:
        return
    status, command = search(args[0], args[1:])

    if not command:
        return

    if status == ShellInfo.EXIT:
        return 0
    if user_vars.get("DEBUG", "false") == "true":
        print(command, args)
    if callable(command):
        command(*args)
        return
    if status == ShellInfo.OK:
        execute(command, args)


def input_routine():
    while True:
        write("$ ")

        # Wait for user input
        cmd = input()
        args = cmd_split(cmd)
        stat = common_routine(args)
        if stat == 0:
            return 0
    return

def execute_routine(program, args):
    if not exists(program):
        write(f"{program} not found\n")
        exit(1)

    with open(program) as file:
        data = file.readlines()

    for i, val in enumerate(args):
        user_vars[str(i)] = val

    for lineno, line in enumerate(data):
        if lineno == 0 and line.startswith("#!"):
            continue

        if line.startswith("#") or line.startswith("//"):
            continue
        args = cmd_split(line)
        if common_routine(args) == 0:
            return 0
        
def main(program=None, args=None):
    # Uncomment this block to pass the first stage
    # sys.stdout.write("$ ")
    # sys.stdout.flush()
    if not program:
        return input_routine()
    return execute_routine(program, args)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            exit(main())
        else:
            main(sys.argv[1], sys.argv[2:])
    except (KeyboardInterrupt, EOFError):
        pass
