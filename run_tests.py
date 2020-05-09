#!/usr/bin/env python
from __future__ import print_function
from distutils.spawn import find_executable
import os
import shutil
import sys
import tempfile

import pytest
from mongobox import MongoBox

from setup_admin_user import create_admin


def read_or_set(key, default):
    if key not in os.environ:
        os.environ[key] = default
    return os.environ[key]


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MONGO_HOST = read_or_set('MONGO_HOST', '127.0.0.1')
MONGO_PORT = int(read_or_set('MONGO_PORT', '27018'))
MONGO_PORT_AUTH = int(read_or_set('MONGO_PORT_AUTH', '27019'))
MONGO_ADMIN = read_or_set('MONGO_ADMIN', 'admin')
MONGO_ADMIN_PASS = read_or_set('MONGO_ADMIN_PASS', 'pass')
MONGOD_BIN = find_executable('mongod')
TMP_DIR = tempfile.gettempdir()


def _get_mongo_paths():
    paths = os.path.join(TMP_DIR, 'data'), os.path.join(TMP_DIR, 'data_auth')
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
    return paths


def run(args=None):
    print('\nStarting mongo servers')
    args = args or []
    path, path_auth = _get_mongo_paths()
    params = dict(mongod_bin=MONGOD_BIN, db_path=path, port=MONGO_PORT)
    mongobox = MongoBox(**params)
    params.update(dict(auth=True, db_path=path_auth, port=MONGO_PORT_AUTH))
    mongoboxAuth = MongoBox(**params)
    status = False
    statusAuth = False

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
        print(' - admin user on server auth...', end=' '), sys.stdout.flush()
        create_admin(
            host=MONGO_HOST,
            port=MONGO_PORT_AUTH,
            name=MONGO_ADMIN,
            password=MONGO_ADMIN_PASS
        )
        print('OK\n'), sys.stdout.flush()

        # run pytest
        pytest.main(*args)
    except Exception:
        raise
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
