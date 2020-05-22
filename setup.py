# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


BASE_DIR = os.path.dirname(__file__)
VERSION = '2.2.2'
URL = 'https://github.com/fvalverd/AutoApi'
DOWNLOAD_URL = '{}/tarball/v{}'.format(URL, VERSION)
REQUIREMENTS = os.path.join(BASE_DIR, 'requirements.txt')
REQUIREMENTS_DEV = os.path.join(BASE_DIR, 'requirements-dev.txt')


class RunTests(TestCommand):
    user_options = [
        ('runtests-args=', 'a', "Arguments to pass to pytest (ex: '-sv')")
    ]

    def initialize_options(self):
        self.runtests_args = ''
        TestCommand.initialize_options(self)

    def run_tests(self):
        import shlex
        from run_tests import run
        run(args=[shlex.split(self.runtests_args)])


def read_requirements(path):
    if not os.path.exists(path):
        return None
    with open(path) as file:
        return file.read()


setup(
    cmdclass={'run_tests': RunTests},
    download_url=DOWNLOAD_URL,
    entry_points={'console_scripts': ['autoapi = auto_api.__main__:cli']},
    install_requires=read_requirements(REQUIREMENTS),
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={'': [REQUIREMENTS]},
    tests_require=read_requirements(REQUIREMENTS_DEV),
    url=URL,
    version=VERSION
)
