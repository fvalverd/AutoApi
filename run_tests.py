#!/usr/bin/env python
from __future__ import print_function
from distutils.spawn import find_executable
import os
import shutil
import subprocess
import sys
import tempfile

import pytest
import mongobox
from pymongo import MongoClient


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


def update_admin():
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT_AUTH)
    data = dict(pwd=MONGO_ADMIN_PASS, roles=[{'role': 'root', 'db': 'admin'}])
    client.admin.command('createUser', MONGO_ADMIN, **data)
    client.close()
    python_bin = find_executable('python')
    envs = {
        'MONGO_HOST': MONGO_HOST,
        'MONGO_PORT': str(MONGO_PORT_AUTH),
        'MONGO_ADMIN': MONGO_ADMIN,
        'MONGO_ADMIN_PASS': MONGO_ADMIN_PASS
    }
    subprocess.Popen([python_bin, '-m', 'auto_api', 'update-admin'], env=envs)


def fix_mongo_42():
    pos = mongobox.mongobox.DEFAULT_ARGS.index("--smallfiles")
    if pos >= 0:
        mongobox.mongobox.DEFAULT_ARGS.pop(pos)


def run(args=None):
    fix_mongo_42()
    print('\nStarting mongo servers')
    args = args or []
    path, path_auth = _get_mongo_paths()
    default_params = dict(prealloc=True, mongod_bin=MONGOD_BIN)
    params = dict(db_path=path, port=MONGO_PORT, **default_params)
    mongoboxNoAuth = mongobox.MongoBox(**params)
    params.update(auth=True, db_path=path_auth, port=MONGO_PORT_AUTH)
    mongoboxAuth = mongobox.MongoBox(**params)
    status = False
    statusAuth = False

    try:
        # start server
        print(' - server...', end=' '), sys.stdout.flush()
        mongoboxNoAuth.start()
        status = True
        print('OK')

        # start auth server
        print(' - server auth...', end=' '), sys.stdout.flush()
        mongoboxAuth.start()
        print('OK')
        statusAuth = True
        print(' - admin user on server auth...', end=' '), sys.stdout.flush()
        update_admin()
        print('OK\n'), sys.stdout.flush()

        # run pytest
        exit(pytest.main(*args))
    except Exception:
        exit(10)
    finally:
        # stop servers
        if status:
            print('\n\nStoping mongo servers:')
            print(' - server...', end=' '), sys.stdout.flush()
            mongoboxNoAuth.stop()
            print('OK')
            if statusAuth:
                print(' - server auth...', end=' '), sys.stdout.flush()
                mongoboxAuth.stop()
                print('OK\n'), sys.stdout.flush()


if __name__ == '__main__':
    run()
