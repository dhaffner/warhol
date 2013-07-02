'''
Helper functions.
'''
__all__ = ['fullpath', 'listdir', 'which']

import functools
import os

from functools import reduce


def compose(*funcs):
    """
    Compose a sequence of functions into one single function.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


fullpath = compose(os.path.abspath, os.path.expanduser)


def listdir(path):
    """
    Return a list of files in the given path. Files are returned with
    full paths.
    """
    path = fullpath(path)
    join = functools.partial(os.path.join, path)
    return map(join, os.listdir(path))


def which(executable):
    """
    A wrapper around the shell function 'which', used to determine
    whether (and where) an executable exists.
    """
    return executable and \
        not os.system('\which -s {}'.format(executable.split(' ')[0]))
