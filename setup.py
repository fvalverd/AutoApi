# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


VERSION = '1.0.3'


class RunTests(TestCommand):
    user_options = [
        ("runtests-args=", "a", "Arguments to pass to pytest (ex: '-sv')")
    ]

    def initialize_options(self):
        self.runtests_args = ''
        TestCommand.initialize_options(self)

    def run_tests(self):
        import shlex
        from run_tests import run
        run(args=[shlex.split(self.runtests_args)])


setup(
    name='auto_api',
    version=VERSION,
    description='Automatic API REST',
    long_description="""
AutoApi was created to not wasting time to developing an API REST at the
project start. Has an authentication system to provided secure data based on
MongoDB
""",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='api rest authentication mongodb automatic web flask json',
    author='Felipe Valverde Campos',
    author_email='felipe.valverde.campos@gmail.com',
    url='https://github.com/fvalverd/AutoApi',
    download_url='https://github.com/fvalverd/AutoApi/tarball/v1.0.3',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click>=6.7',
        'Flask>=1.0.2',
        'Flask-Cors>=3.0.7',
        'pymongo>=3.7.2,<4'
    ],
    tests_require=[
        'mock',
        'mongobox>=0.1.8',
        'pytest',
        'pytest-cov'
    ],
    cmdclass={'run_tests': RunTests},
    entry_points={
        'console_scripts': [
            'autoapi = auto_api.__main__:main'
        ]
    }
)
