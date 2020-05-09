#!/usr/bin/env python
from __future__ import print_function
import os
import sys

from pymongo import MongoClient

from auto_api.mongodb import update_roles, ADMIN_KEYS, MONGO_KEYS

if sys.version_info >= (3, 0):
    from unittest import mock
else:
    import mock


def _upgrade_to_autoapi_admin(host, port, name, password):
    config = {
        MONGO_KEYS['host']: host,
        MONGO_KEYS['port']: port,
        ADMIN_KEYS['name']: name,
        ADMIN_KEYS['password']: password
    }
    mocked_app = mock.Mock(config=config)
    return update_roles(
        mocked_app, api='admin', user=name, roles={'admin': True}
    )


def create_admin(host, port, name, password):
    client = MongoClient(host=host, port=port)
    data = dict(pwd=password, roles=[{'role': 'root', 'db': 'admin'}])
    client.admin.command('createUser', name, **data)
    client.close()
    return _upgrade_to_autoapi_admin(host, port, name, password)


if __name__ == '__main__':
    autoapi_admin_was_marked = _upgrade_to_autoapi_admin(
        host=os.environ[MONGO_KEYS['host']],
        port=int(os.environ['MONGO_PORT_AUTH']),
        name=os.environ[ADMIN_KEYS['name']],
        password=os.environ[ADMIN_KEYS['password']]
    )
    if not autoapi_admin_was_marked:
        print("ERROR: MongoDB root user couldn't be marked as Auto-Api admin")
        exit(1)

    print('MongoDB root user marked as Auto-Api admin !')
