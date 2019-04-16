# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


VERSION = '2.0.1'


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


setup(
    version=VERSION,
    download_url='https://github.com/fvalverd/AutoApi/tarball/v2.0.1',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[
        'click>=6.7',
        'Flask>=1.0.2',
        'Flask-Cors>=3.0.7',
        'pymongo>=3.7.2,<4'
    ],
    tests_require=[
        'mock;python_version<"3.0"',
        'mongobox>=0.1.8',
        'pytest',
        'pytest-cov'
    ],
    cmdclass={'run_tests': RunTests},
    entry_points={
        'console_scripts': ['autoapi = auto_api.__main__:main']
    }
)
