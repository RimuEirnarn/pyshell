"""PyShell"""

import sys
import os
from os.path import join as path_join, exists
from shlex import split as cmd_split
from enum import IntEnum, unique
from functools import cache
from subprocess import Popen
from types import FunctionType
import builtin_fns as commands


def execute(program, args):
    """Execute a program with arguments."""
    with Popen(
        args, executable=program, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
    ) as proc:
        proc.wait()


def execute_pipe(program, args, stdin, stdout, stderr):
    """Execute a program with arguments and pipe stdin/stdout."""
    with Popen(
        args, executable=program, stdin=stdin, stdout=stdout, stderr=stderr
    ) as proc:
        proc.wait()


@cache
def cache_query(base):
    """Cache a query."""
    return query(base)


def query(base):
    """Query a program based on PATH."""
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
    """Shell Information"""

    OK = 0
    EXIT = -1
    CMD_NOT_FOUND = -2
    ERROR = -3


user_vars = {}
environ = os.environ

cmds = {
    sym.replace("do_", "", 1): getattr(commands, sym)
    for sym in dir(commands)
    if "do_" in sym and callable(getattr(commands, sym))
}


def write(*args, sep=" "):
    """Write arguments to stdout (akin to print function)"""
    sys.stdout.write(sep.join(args))
    sys.stdout.flush()


def search(base: str) -> tuple[ShellInfo, str | FunctionType]:
    """Search for a command."""
    if not base:
        return ShellInfo.OK, ""
    if base in cmds:
        return ShellInfo.OK, cmds[base]

    status, cmd = query(base)

    if status == ShellInfo.CMD_NOT_FOUND:
        write(f"{base}: command not found\n")
        return ShellInfo.CMD_NOT_FOUND, ""
    return ShellInfo.OK, cmd


def common_routine(args):  # pylint: disable=inconsistent-return-statements
    """Common Routine for Shell"""
    if not args:
        return
    status, command = search(args[0])

    if not command:
        return

    if status == ShellInfo.EXIT:
        return ShellInfo.EXIT
    if user_vars.get("DEBUG", "false") == "true":
        print(command, args)

    if callable(command):
        return command(*args)
    if status == ShellInfo.OK:
        execute(command, args)

    return


def input_routine():
    """Input routine (command line interface)."""
    while True:
        write("$ ")

        # Wait for user input
        cmd = input()
        args = cmd_split(cmd)
        stat = common_routine(args)
        if stat == ShellInfo.EXIT:
            break
    return 0


def execute_routine(program, args):
    """Execute routine (exec() a program from file)"""
    if not exists(program):
        write(f"{program} not found\n")
        return 1

    with open(program, encoding="utf-8") as file:
        data = file.readlines()

    for i, val in enumerate(args):
        user_vars[str(i)] = val

    for lineno, line in enumerate(data):
        if lineno == 0 and line.startswith("#!"):
            continue

        if line.startswith("#") or line.startswith("//"):
            continue
        args = cmd_split(line)
        if common_routine(args) == ShellInfo.EXIT:
            break

    return 0


def main(program=None, args=None):
    """Main routine."""
    if not program:
        return input_routine()
    return execute_routine(program, args)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            sys.exit(main())
        else:
            main(sys.argv[1], sys.argv[2:])
    except (KeyboardInterrupt, EOFError):
        pass
