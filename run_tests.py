#!/usr/bin/env python
from __future__ import print_function
import imp
import os
import shutil
import sys

import pytest
from pymongo import MongoClient
from mongobox import MongoBox


MONGO_PORT, MONGO_AUTH_PORT = 27018, 27019
AUTOAPI_SETTINGS_FILE = 'tests.cfg.default'


def run(args=None):
    if args is None:
        args = []

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

    # create temporal directory
    TMP_DIR = os.path.join(CURRENT_DIR, '.tmp')
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    DB_PATH = os.path.join(TMP_DIR, 'data')
    DB_PATH_AUTH = os.path.join(TMP_DIR, 'data_auth')

    if os.path.exists(DB_PATH_AUTH):
        shutil.rmtree(DB_PATH_AUTH)

    # set autoapi environment variable for config
    os.environ['AUTOAPI_SETTINGS'] = os.path.join(
        CURRENT_DIR, AUTOAPI_SETTINGS_FILE
    )

    def create_admin():
        print(' - admin user on server auth...', end=' ')
        sys.stdout.flush()

        # config module file
        config = imp.load_source('module.name', os.environ['AUTOAPI_SETTINGS'])

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

    mongobox = MongoBox(mongod_bin='mongod', db_path=DB_PATH, port=MONGO_PORT)
    mongoboxA = MongoBox(
        mongod_bin='mongod', auth=True,
        db_path=DB_PATH_AUTH, port=MONGO_AUTH_PORT
    )

    status, statusA = False, False
    errno = 1
    try:
        print('\nStarting mongo servers')

        # start server
        print(' - server...', end=' ')
        sys.stdout.flush()
        mongobox.start()
        status = True
        print('OK')

        # start auth server
        print(' - server auth...', end=' ')
        sys.stdout.flush()
        mongoboxA.start()
        print('OK')
        statusA = True
        create_admin()
        print('\n')
        sys.stdout.flush()

        errno = pytest.main(*args)
    finally:
        # stop servers
        if status:
            print('\n\nStoping mongo servers:')
            print(' - server...', end=' ')
            sys.stdout.flush()
            mongobox.stop()
            print('OK')
            if statusA:
                print(' - server auth...', end=' ')
                sys.stdout.flush()
                mongoboxA.stop()
                print('OK')
    return errno


if __name__ == '__main__':
    sys.exit(run())
