from setuptools import setup

setup(name='warhol',
      version='0.1',
      description='A small server and browser extension pairing for adding styles and scripts to a page on the fly.',
      url='http://github.com/dhaffner/warhol',
      author='Dustin Haffner',
      author_email='dh@xix.org',
      license='MIT',
      packages=['warhol'],
      scripts=['bin/warhol'],
      install_requires=['gunicorn'],
      zip_safe=False)
