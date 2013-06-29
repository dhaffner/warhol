import json
import os

from helpers import fullpath, which


def check(filename):

    with open(fullpath(filename), 'r') as f:
        config = json.load(f)

    # Check for compilers
    for extension, command in config['compilers'].iteritems():
        assert which(command), 'error: {} executable not found'.format(command)

    # Check paths -- REFACTOR
    # kinds = operator.itemgetter('js', 'css')
    # paths = flatten(itertools.imap(operator.itemgetter('paths'),
    #                                kinds(self.options)))
    # paths = itertools.imap(normalize, paths)
    # for path in itertools.ifilterfalse(os.path.exists, paths):
    #     print('path not found:', path)

    # print('ok - paths')

    assert which('gunicorn'), 'error: gunicorn not found'

    if 'gunicorn' in config:
        location = config['gunicorn'].get('bind')
        if location and \
           not os.system('\lsof -i "TCP@{}" >> /dev/null'.format(location)):
            print('bind location {} already in use'.format(location))

    print('ok: {}'.format(filename))
