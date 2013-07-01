__all__ = ['init']

import json
import os
import os.path
import subprocess

from collections import defaultdict
from helpers import fullpath, listdir, which


def init(filename=None, options=None, **kwargs):
    """
    Initialize an HTTP app with the specified settings and return its
    callable.
    """

    # Build the config dictionary. Prioritize settings, config, and kwargs
    # in that order.
    config = {}
    with open(fullpath(filename), 'r') as f:
        config.update(json.load(f))

    if options is not None:
        config.update(options)

    if kwargs is not None:
        config.update(kwargs)

    types, binds, files = {}, {}, defaultdict(set)

    for section, contents in config.iteritems():
        if 'extensions' not in contents:
            continue

        extensions = set(contents['extensions'].keys())

        if 'bind' in contents:
            key = contents['bind']
            binds[key] = section
            extensions.add(key)

        for path in contents.get('paths', []):
            splits = map(os.path.splitext, listdir(path))
            files[section].update((head, tail) for (head, tail) in splits if tail in extensions)

        for extension, command in contents['extensions'].iteritems():
            if extension in types:  # ignore duplicates
                continue

            print(extension, command)
            # Allow null commands, allow commands whose executables
            # exist.
            if not command or which(command):
                types[extension] = (section, command)

    def run(filename, command):
        if not command:
            with open(filename, 'r') as f:
                return tuple(iter(f.readline, b''))

        args = command.split(' ') + [filename]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        return tuple(iter(proc.stdout.readline, b''))

    def app(environ, respond):
        headers = {'Content-type': 'text/plain'}
        domain, extension = os.path.splitext(environ['PATH_INFO'])
        lines = ('', )

        content_type = binds.get(extension)

        if content_type:
            headers['Content-type'] = content_type

            for (head, tail) in files[content_type]:
                if not head.endswith(domain):
                    continue

                _, command = types[tail]
                lines = run(head + tail, command)
                break

        if 'Content-length' not in headers:
            headers['Content-length'] = reduce(lambda x, y: x + len(y), lines, 0)

        respond('200 OK', headers.iteritems())
        return iter(lines)

    return app
