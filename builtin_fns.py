"""Builtin functions for PyShell"""

from functools import wraps
from general import ShellInfo, write, user_vars, environ
from os import chdir
from os.path import expanduser, exists
from inspect import getmodule, getdoc


def get_module_dir():
  """Retrieves the current module's directory."""
  return getmodule(get_module_dir)

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
    """Exit the shell.

    $ exit"""
    return ShellInfo.EXIT


def do_set(*args):
    """Set a user variable.

    $ set something=value"""
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
    """Export a variable.

    $ export something=value"""
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
    """Unset a variable.

    $ unset variable"""
    arg = args[1]
    if not arg in user_vars:
        write(f"{arg} was not in variables\n")
        return ShellInfo.OK
    del user_vars[arg]


@insufficient_arg
def do_unexport(*args):  # pylint: disable=inconsistent-return-statements
    """Unset an environment variable.

    $ unexport variable"""
    arg = args[1]
    if not arg in environ:
        write(f"{arg} was not in environ\n")
        return ShellInfo.OK
    del environ[arg]

def do_cd(*args):
    """Change current directory

    $ cd [directory]"""
    if len(args) == 1:
        path = expanduser("~")
    else:
        path = expanduser(args[1])

    if not exists(path):
        write(f"{path} does not exists.\n")
        return ShellInfo.ERROR

    try:
        chdir(path)
    except Exception as exc:
        write(f"cd: {path}: {type(exc).__name__}: {exc!s}\n")
        return ShellInfo.ERROR
    return ShellInfo.OK

def do_help(*args):
    """Get some help

    $ help [builtin-name]"""
    module = get_module_dir()
    funcs = {
        a.replace("do_", "", 1) : getattr(module, a)
        for a in dir(module)
            if a.startswith("do_")
    }
    if len(args) == 1:
        sums = [
            (getdoc(a) or "<no help>\n")
                .split("\n")[0]
            for _, a in funcs.items()
        ]
        helpstr = f"PyShell Builtin Help Document"
        write(f"{helpstr}\n{'='*len(helpstr)}\n")
        for i, name in enumerate(funcs):
            write(f"{name: <10}\t: {sums[i]}\n")
        return ShellInfo.OK
    name = args[1]
    if not name in funcs:
        write(f"{name} is not a builtin function.\n")
        return ShellInfo.CMD_NOT_FOUND
    write(getdoc(funcs[name])+"\n")
    return ShellInfo.OK

def do_undefined(*_):
    return ShellInfo.OK

def do_pass(*_):
    "Do nothing."
    return ShellInfo.OK
