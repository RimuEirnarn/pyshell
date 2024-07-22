"""Builtin functions for PyShell"""

from functools import wraps
from general import ShellInfo, write, user_vars, environ


def insufficient_arg(func):
    """Decorator for functions that require at least one argument"""

    @wraps(func)
    def wrapper(*args):
        if not args or len(args) == 1:
            write("Insufficient argument\n")
            return ShellInfo.ERROR
        return func(*args)

    return wrapper


def do_exit(*_):
    """Exit the shell."""
    return ShellInfo.EXIT


def do_set(*args):
    """Set a user variable."""
    if not args or len(args) == 1:
        for key, value in user_vars.items():
            write(f"set {key}={value!r}\n")
        return ShellInfo.OK
    arg = args[1]
    if not "=" in arg:
        write("Syntax error, expecting '='\n")
        return ShellInfo.ERROR

    name, value = arg.split("=", 1)
    user_vars[name.lstrip().rstrip()] = value.lstrip().rstrip()
    return ShellInfo.OK


def do_export(*args):
    """Export a variable."""
    if not args or len(args) == 1:
        for key, value in environ.items():
            write(f"export {key}={value!r}\n")
        return ShellInfo.OK

    arg = args[1]

    if not "=" in arg:
        write("Syntax error, expecting '='\n")
        return ShellInfo.ERROR

    name, value = arg.split("=", 1)
    environ[name.lstrip().rstrip()] = value.lstrip().rstrip()
    return ShellInfo.OK


@insufficient_arg
def do_unset(*args):  # pylint: disable=inconsistent-return-statements
    """Unset a variable."""
    arg = args[1]
    if not arg in user_vars:
        write(f"{arg} was not in variables\n")
        return ShellInfo.OK
    del user_vars[arg]


@insufficient_arg
def do_unexport(*args):  # pylint: disable=inconsistent-return-statements
    """Unset an environment variable."""
    arg = args[1]
    if not arg in environ:
        write(f"{arg} was not in environ\n")
        return ShellInfo.OK
    del environ[arg]
