def test_config():
    pass


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
