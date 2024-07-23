"""General import modules"""

import sys
import os
from os.path import join as path_join
from enum import IntEnum, unique
from functools import cache
from subprocess import Popen

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


def write(*args, sep=" "):
    """Write arguments to stdout (akin to print function)"""
    sys.stdout.write(sep.join(args))
    sys.stdout.flush()
