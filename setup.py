# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='auto_api',
    version=version,
    description="Automatic API REST",
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
    download_url='https://github.com/fvalverd/AutoApi/tarball/0.0.1',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask==0.10.1",
        "flask-cors==2.0.0",
        "pymongo==2.8",
        "pyOpenSSL==17.0.0"
    ],
    tests_require=['nose'],
    test_suite="tests",
    entry_points="""
    # -*- Entry points: -*-
    """,
)
