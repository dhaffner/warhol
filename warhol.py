#!/usr/bin/env python
from __future__ import print_function

__all__ = ['init', 'app']

import collections
import functools
import itertools
import json
import operator
import os
import re
import signal
import subprocess
import sys

NAME = 'warhol'
CONFIG = '~/.warhol/config'


#
#   Helper functions
#


def empty(generator):
    """Return True or False depending on whether generator is empty."""
    try:
        next(generator)
        return False

    except StopIteration:
        return True


def domain(filename, extensions=('\w+', )):
    """Extract and return the domain portion of the requested filename.
    Optionally limit only to those filenames which have one of the
    specified extensions.
    """
    pattern = '\W?([^\.]+\.[^\.]+)\.(?:{})$'.format('|'.join(extensions))
    iterable = re.finditer(pattern, filename, flags=re.IGNORECASE | re.LOCALE)

    for match in iterable:
        hostname, = match.groups(0)
        return hostname


def findfiles(filename, extensions, dirs):
    """Return an iterable of files which map to the given filename (likely
    from a request) and have the specified extensions. Limit the search to
    the specified dirs.
    """
    hostname = domain(filename, extensions)

    if hostname is None or \
       (extensions and not len(extensions)) or \
       (dirs and not len(dirs)):  # fail somehow
        return tuple()

    match = matches('\.?{}\.({})$'.format(hostname, '|'.join(extensions)))
    files = itertools.ifilter(match, flatten(itertools.imap(listdir, dirs)))
    valid = lambda f: not empty(itertools.ifilter(f.endswith, extensions))
    return itertools.ifilter(valid, files)


def first(iterable):
    """Return the first item from the given iterable."""
    try:
        return next(iterable)
    except TypeError:
        return next(iter(iterable))


# Flatten an iterable of iterables one level of nesting.
flatten = itertools.chain.from_iterable


def listdir(path):
    """Return a list of files in the given path. Files are returned with
    full and absolute paths.
    """
    fullpath = normalize(path)
    join = functools.partial(os.path.join, fullpath)
    return itertools.imap(join, os.listdir(fullpath))


def matches(pattern):
    """Return a boolean test function for the given regular expression."""
    compiled = re.compile(pattern, flags=re.IGNORECASE | re.LOCALE)
    return lambda string: bool(compiled.search(string))


def normalize(filename):
    """Normalize a filename to a full path."""
    return os.path.abspath(os.path.expanduser(filename))


def which(executable):
    if executable is None or len(executable) == 0:
        return False

    if executable.find(' ') >= 0:
        executable = executable.split(' ')[0]

    return not os.system('\which -s {}'.format(executable))


#
#   Application functions
#


class CheckConfig(object):
    def __init__(self, filename=CONFIG, options=None):
        if options is not None:
            self.options = {}.update(options)

        else:
            self.options = self.config(filename)

        self.check()

    def check(self):
        # config already checked on init
        keys = ('js', 'css', 'compilers')
        for k in itertools.ifilterfalse(self.options.has_key, keys):
            print('error - expected to find key {} in config'.format(k))

        else:
            self.compilers()
            self.paths()

        if self.gunicorn():
            self.bind()

        print('done')

    def config(self, filename=None):
        try:
            with open(normalize(filename), 'Ur') as f:
                return json.load(f)

        except:
            print('error - could not open and parse:', filename)
            exit()

        finally:
            print('ok -', filename)

    def compilers(self):
        for extension, command in self.options['compilers'].iteritems():
            if not which(command):
                print('error - command for {}'.format(extension),
                      ' not found in path: {}'.format(command))
        else:
            print('ok - compilers')

    def paths(self):
        kinds = operator.itemgetter('js', 'css')
        paths = flatten(itertools.imap(operator.itemgetter('paths'),
                                       kinds(self.options)))
        paths = itertools.imap(normalize, paths)
        for path in itertools.ifilterfalse(os.path.exists, paths):
            print('path not found:', path)

        print('ok - paths')

    def gunicorn(self):
        if not which('gunicorn'):
            print('error - gunicorn not found')

        elif 'gunicorn' not in self.options:
            print('error - no gunicorn options specified')

        else:
            print('ok - gunicorn')
            return True

        return False

    def bind(self):
        location = self.options['gunicorn'].get('bind')
        if location is None:
            print('error - no bind location specified for gunicorn (bind)')

        if not os.system('\lsof -i "TCP@{}" >> /dev/null'.format(location)):
            print('error - bind location {} already in use'.format(location))
            return False

        else:
            print('ok - bind location {}'.format(location))

        return True


def sigint(proc, *args):
    """Kill gunicorn when we get a sigint."""
    proc.terminate()


def gunicorn(func, **options):
    """Launch gunicorn to handle the worker threads."""
    name = '{}:{}'.format(NAME, func.__name__)

    defaults = {'name': NAME, 'bind': '127.0.0.1:1928', 'workers': 2,
                'log-level': 'error'}

    for key in defaults.iterkeys():
        if key not in options:
            options[key] = defaults[key]

    args = itertools.starmap('--{}={}'.format, options.iteritems())
    command = ('gunicorn', '--preload') + (tuple(args) + (name, ))
    proc = subprocess.Popen(command,
                            stdout=sys.stdout, stdin=sys.stdin, shell=False)
    print('{name} ~ {bind}'.format(**options))
    return proc


def init(filename=CONFIG, options=None, **kwargs):
    """Initialize an HTTP app with the specified settings and return its
    callable.

    filename (and thus all configuration) defaults to CONFIG.
    """
    config = {}

    with open(normalize(filename), 'Ur') as f:
        try:
            foptions = json.load(f)
            config.update(foptions)
        except:
            pass

    if options is not None:
        config.update(options)

    if kwargs is not None:
        config.update(kwargs)

    if not ('css' in config and 'js' in config):
        print('css and js settings missing from config')
        exit(0)

    compilers = config.get('compilers', {})

    seen = set()
    for extension, command in compilers.items():
        executable = first(command.split(' '))
        if executable in seen:
            continue

        if os.system('which -s {}'.format(executable)) != 0:
            del compilers[extension]

        seen.add(executable)

    del seen, extension, command

    def compile_(filename, extension):
        command = tuple(compilers[extension].split(' ')) + (filename, )
        return subprocess.Popen(command, stdout=subprocess.PIPE)

    setting = collections.namedtuple('setting', ['js', 'css'])

    extensions = setting(tuple(config['js']['extensions']),
                         tuple(config['css']['extensions']))

    paths = setting(tuple(config['js']['paths']),
                    tuple(config['css']['paths']))

    isjavascript = matches('.{}$'.format('|'.join(extensions.js)))
    iscss = matches('.{}$'.format('|'.join(extensions.css)))

    def app(environ, respond):
        headers = {}
        name = environ['PATH_INFO']
        if iscss(name):
            preferences, dirs = extensions.css, paths.css
            headers['Content-type'] = 'text/css'

        elif isjavascript(name):
            preferences, dirs = extensions.js, paths.js
            headers['Content-type'] = 'text/javascript'

        else:
            preferences, dirs = tuple(), tuple()
            headers['Content-type'] = 'text/plain'

        files = findfiles(name, preferences, dirs)
        try:
            filename = first(files)
            extension = filename.split('.')[-1].lower()
            if extension in compilers:
                proc = compile_(filename, extension)
                lines = tuple(iter(proc.stdout.readline, b''))

            else:
                with open(filename, 'Ur') as f:
                    lines = tuple(iter(f.readline, b''))

        except StopIteration:
            lines = ('', )

        if 'Content-length' not in headers:
            headers['Content-length'] = \
                reduce(lambda x, y: x + len(y), lines, 0)

        respond('200 OK', headers.iteritems())
        return iter(lines)

    return config, app


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        command = args[1]
        if command.endswith('check'):
            if len(args) < 3:
                exit('specify a configuration file')

            else:
                filename = args[2]
                CheckConfig(filename)

            if not command.startswith('-'):
                exit(0)

            else:
                print()

        else:
            filename = args[1]

    else:
        filename = CONFIG

else:
    filename = CONFIG

config, app = init(filename)

if __name__ == '__main__':
    print('configuration: {}'.format(filename))
    options = config.get('gunicorn', {})
    workers = gunicorn(app, **options)
    signal.signal(signal.SIGINT, functools.partial(sigint, workers))
    workers.wait()
    exit(0)
