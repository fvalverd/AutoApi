#!/usr/bin/env python
from __future__ import print_function
import imp
import os
import shutil
import sys

import pytest
from pymongo import MongoClient
from mongobox import MongoBox


SETTINGS_ENV = 'AUTOAPI_SETTINGS'
AUTOAPI_SETTINGS_FILE = 'tests.cfg.default'
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TMP_DIR = os.path.join(CURRENT_DIR, '.tmp')
MONGO_PORT, MONGO_AUTH_PORT = 27018, 27019


# set autoapi setting environment variable
os.environ[SETTINGS_ENV] = os.path.join(CURRENT_DIR, AUTOAPI_SETTINGS_FILE)


def _get_mongo_paths():
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)
    paths = os.path.join(TMP_DIR, 'data'), os.path.join(TMP_DIR, 'data_auth')
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
    return paths


def _get_config_module():
    return imp.load_source('module.name', os.environ[SETTINGS_ENV])


def _create_admin():
    print(' - admin user on server auth...', end=' ')
    sys.stdout.flush()
    config = _get_config_module()
    client = MongoClient(port=MONGO_AUTH_PORT)
    client.admin.command(
        'createUser',
        config.MONGO_ADMIN,
        pwd=config.MONGO_ADMIN_PASS,
        roles=[
            {'role': 'userAdminAnyDatabase', 'db': 'admin'},
            'readWriteAnyDatabase'
        ],
        customData={'roles': ['admin']}
    )
    client.close()
    print('OK')


def run(args=None):
    print('\nStarting mongo servers')
    args = args or []
    db_path, db_path_auth = _get_mongo_paths()
    params = dict(mongod_bin='mongod', db_path=db_path, port=MONGO_PORT)
    mongobox = MongoBox(**params)
    params.update(dict(auth=True, db_path=db_path_auth, port=MONGO_AUTH_PORT))
    mongoboxAuth = MongoBox(**params)
    status = statusAuth = False
    try:
        # start server
        print(' - server...', end=' '), sys.stdout.flush()
        mongobox.start()
        status = True
        print('OK')

        # start auth server
        print(' - server auth...', end=' '), sys.stdout.flush()
        mongoboxAuth.start()
        print('OK')
        statusAuth = True
        _create_admin()
        print('\n'), sys.stdout.flush()

        pytest.main(*args)
    finally:
        # stop servers
        if status:
            print('\n\nStoping mongo servers:')
            print(' - server...', end=' '), sys.stdout.flush()
            mongobox.stop()
            print('OK')
            if statusAuth:
                print(' - server auth...', end=' '), sys.stdout.flush()
                mongoboxAuth.stop()
                print('OK')


if __name__ == '__main__':
    run()
