"""PyShell"""

import sys
from os.path import exists
from shlex import split as cmd_split
from types import FunctionType
from argh import dispatch_command, arg
import builtin_fns as commands
from general import user_vars, execute, ShellInfo, write, query

__version__ = "0.0.1"

cmds = {
    sym.replace("do_", "", 1): getattr(commands, sym)
    for sym in dir(commands)
    if "do_" in sym and callable(getattr(commands, sym))
}


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


@arg("program", help="pyshell (.pyshell) files")
@arg("args", help="pyshell arguments")
@arg("-v", "--version", help="PyShell's version")
def main(
    program=None, *args, version=False
):  # pylint: disable=keyword-arg-before-vararg
    """Another Python Shell"""
    if version:
        print(f"PyShell v{__version__}")
        return
    if not program:
        sys.exit(input_routine())
        return  # pylint: disable=unreachable
    sys.exit(execute_routine(program, args))


if __name__ == "__main__":
    try:
        dispatch_command(main, old_name_mapping_policy=False)
    except (KeyboardInterrupt, EOFError):
        pass
