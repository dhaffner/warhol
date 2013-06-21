#!/usr/bin/env python
from __future__ import print_function

__all__ = ['init']

import json
import os
import os.path
import subprocess

from operator import itemgetter

from helpers import first, findfiles, fullpath


'''
When a request comes in:

1 check its filename: should be like www.github.com.js
2 get all extensions which map (compile to) js from the config: [coffee, elm, etc]
3 take first matching filename of form www.github.com.ext where ext in above list
4 run compiler on said file
5 return it as http response
'''


def init(filename=None, options=None, **kwargs):
    """Initialize an HTTP app with the specified settings and return its
    callable.

    filename (and thus all configuration) defaults to CONFIG.
    """

    # Build the config dictionary. Prioritize settings, config, and kwargs
    # in that order.
    config = {}
    with open(fullpath(filename), 'Ur') as f:
        config.update(json.load(f))

    if options is not None:
        config.update(options)

    if kwargs is not None:
        config.update(kwargs)

    if not ('styles' in config and 'scripts' in config):
        print('Error: css and js settings missing from config')
        return

    # For each compiler specified in the config, ensure its executable
    # exist or don't add it.
    compilers = config.get('compilers', {})

    seen = set()
    for extension, command in compilers.items():
        executable = first(command.split(' '))
        if executable in seen:
            continue

        seen.add(executable)
        if os.system('which -s {}'.format(executable)) != 0:
            del compilers[extension]

    #
    #   App-level helpers
    #

    extensions_paths = itemgetter('extensions', 'paths')

    isstyle = config['styles']['extensions'].__contains__

    isscript = config['scripts']['extensions'].__contains__

    def _compile(filename, extension, compilers=config['compilers']):
        command = tuple(compilers[extension].split(' ')) + (filename, )
        return subprocess.Popen(command, stdout=subprocess.PIPE)

    #
    #
    #

    def app(environ, respond):
        headers = {'Content-type': 'text/plain'}

        path = environ['PATH_INFO']

        domain, extension = os.path.splitext(environ['PATH_INFO'])
        domain, extension = domain[1:], extension[1:]

        extensions, paths = [], []

        if isstyle(extension):
            headers['Content-type'] = 'text/css'
            extensions, paths = extensions_paths(config['styles'])

        elif isscript(extension):
            headers['Content-type'] = 'text/javascript'
            extensions, paths = extensions_paths(config['scripts'])

        files = findfiles(path, extensions, paths)
        try:
            filename = first(files)
            base, extension = os.path.splitext(filename)

            extension = extension[1:].lower()
            if extension in compilers:
                proc = _compile(filename, extension)
                lines = tuple(iter(proc.stdout.readline, b''))

            else:  # TODO: filename no compiler, but should ensure it is
                   # CSS or JS.
                with open(filename, 'Ur') as f:
                    lines = tuple(iter(f.readline, b''))

        except StopIteration:
            lines = ('', )

        if 'Content-length' not in headers:
            headers['Content-length'] = \
                reduce(lambda x, y: x + len(y), lines, 0)

        respond('200 OK', headers.iteritems())
        return iter(lines)

    return app
