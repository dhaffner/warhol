'''
Helper functions.
'''

from __future__ import print_function


import functools
import itertools
import os
import os.path
import re


from itertools import chain
from operator import itemgetter

from six.moves import filter, map


def compose(*funcs):
    """
    Compose a sequence of functions into one single function.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


# Flatten an iterable of iterables one level of nesting.
flatten = chain.from_iterable


def first(iterable):
    """
    Return the first item from the given iterable.
    """
    try:
        return next(iterable)
    except TypeError:
        return next(iter(iterable))


def isempty(generator):
    """
    Return True or False depending on whether generator is empty.
    """
    try:
        next(generator)  # will raise StopIteration if empty
        return False

    except StopIteration:
        return True


def matches(pattern):
    """
    Return a boolean test function for the given regular expression.
    """
    compiled = re.compile(pattern, flags=re.IGNORECASE | re.LOCALE)
    return compose(bool, compiled.search)


def getdomain(filename, extensions=('\w+', )):
    """
    Extract and return the domain portion of the requested filename.
    Optionally limit only to those filenames which have one of the
    specified extensions.
    """
    pattern = '\W?([^\.]+\.[^\.]+)\.(?:{})$'.format('|'.join(extensions))
    iterable = re.finditer(pattern, filename, flags=re.IGNORECASE | re.LOCALE)

    for match in iterable:
        hostname, = match.groups(0)
        return hostname


def getfiles(directory, hostname, extensions):
    files = listdir(directory)
    sift = compose(extensions.__contains__, itemgetter(1), os.path.splitext)
    return filter(sift, files)


def findfiles(filename, extensions, dirs):
    """
    Return an iterable of files which map to the given filename (likely
    from a request) and have the specified extensions. Limit the search to
    the specified dirs.
    """
    # Grab the hostname part of this filename.
    # filename looks like 'some.web.address.com.js'
    hostname = getdomain(filename, extensions)

    if hostname is None or \
       (extensions and not len(extensions)) or \
       (dirs and not len(dirs)):  # fail somehow
        return tuple()

    # Build a match testing function based on the given extensions list.

    pattern = '(\.|\/)?{}\.({})$'.format(re.escape(hostname),
                                         '|'.join(map(re.escape, extensions)))
    matcher = matches(pattern)

    def match(fn):
        return matcher(fn)

    # Filter for the files which match for the above function.
    files = filter(match, flatten(map(listdir, dirs)))
    return files

    # Given a filename, ensure that it ends with
    # valid = lambda f: not isempty(filter(f.endswith, extensions))
    #return itertools.ifilter(valid, files)


def listdir(path):
    """
    Return a list of files in the given path. Files are returned with
    full paths.
    """
    path = fullpath(path)
    join = functools.partial(os.path.join, path)
    return itertools.imap(join, os.listdir(path))


fullpath = compose(os.path.abspath, os.path.expanduser)


def which(executable):
    """
    A wrapper around the shell function 'which', used to determine
    whether (and where) an executable exists.
    """
    if executable is None or len(executable) == 0:
        return False

    executable = executable.split(' ')[0]
    return not os.system('\which -s {}'.format(executable))
