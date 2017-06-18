# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.0.3'

setup(
    name='auto_api',
    version=version,
    description='Automatic API REST',
    long_description="""
AutoApi was created to not wasting time to developing an API REST at the
project start. Has an authentication system to provided secure data based on
MongoDB 3.X.
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
        'click==6.7',
        'Flask==0.12.2',
        'flask-cors==3.0.2',
        'pymongo==3.4.0',
        'pyOpenSSL==17.0.0'
    ],
    tests_require=[
        'nose',
        'mock',
        'mongobox==0.1.6'
    ],
    test_suite='run_tests.run',
    entry_points={
        'console_scripts': [
            'autoapi = auto_api.__main__:main'
        ]
    }
)
