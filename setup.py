import os
from setuptools import setup, find_packages
import subprocess

try:
    git_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".git")
    current_tag = subprocess.check_output(['git', '--git-dir', git_path, 'tag']).strip().split('\n')[-1]
except Exception:
    current_tag = '0.0.0'

setup(
    name='ApiSDF',
    version=current_tag,
    description="",
    long_description="""""",
    classifiers=[],
    keywords='api rest',
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
