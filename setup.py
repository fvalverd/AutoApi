# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='AutoApi',
    version=version,
    description="",
    long_description="""""",
    classifiers=[],
    keywords='api rest auth mongodb3',
    author='Felipe Valverde Campos',
    author_email='felipe.valverde.campos@gmail.com',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask==0.10.1",
        "flask-cors==2.0.0",
        "pymongo==2.8",
        "pyOpenSSL==0.14"
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
