from main import ShellInfo, write, user_vars, environ
from functools import wraps

def insufficient_arg(func):
    @wraps(func)
    def wrapper(*args):
        if not args or len(args) == 1:
            write("Insufficient argument\n")
            return ShellInfo.ERROR
        return func(*args)
    return wrapper


def do_exit(*_):
    return ShellInfo.EXIT

def do_set(*args):
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
    if not args or len(args) == 1:
        for key, value in environ.items():
            write(f"export {key}={value!r}\n")
        return ShellInfo.OK

    if not "=" in arg:
        write("Syntax error, expecting '='\n")
        return ShellInfo.ERROR

    name, value = arg.split("=", 1)
    environ[name.lstrip().rstrip()] = value.lstrip().rstrip()
    return ShellInfo.OK

@insufficient_arg
def do_unset(*args):
    arg = args[1]
    if not arg in user_vars:
        write(f"{arg} was not in variables\n")
        return ShellInfo.OK
    del user_vars[arg]

@insufficient_arg
def do_unexport(*args):
    arg = args[1]
    if not arg in environ:
        write(f"{arg} was not in environ\n")
        return ShellInfo.OK
    del environ[arg]
