# -*- coding: utf-8 -*-
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.errors import PyMongoError, OperationFailure


MONGO_KEYS = {'host': 'MONGO_HOST', 'port': 'MONGO_PORT'}
ADMIN_KEYS = {'name': 'MONGO_ADMIN', 'password': 'MONGO_ADMIN_PASS'}


def get_values(config, data):
    return {k: config[v] for k, v in data.iteritems() if v in config}


def get_client(app):
    return MongoClient(**get_values(app.config, MONGO_KEYS))


@contextmanager
def admin(app, client=None, logout=True):
    client = client or get_client(app)
    try:
        client.admin.authenticate(**get_values(app.config, ADMIN_KEYS))
    except PyMongoError:
        pass
    yield client
    if logout:
        client.admin.logout()


def _is_original_admin(app, user):
    return user == app.config[ADMIN_KEYS['name']]


def get_info(app, api, client, user):
    try:
        db = 'admin' if _is_original_admin(app, user) else api
        result = client[api].command('usersInfo', {'user': user, 'db': db})
        return ((result and result.get('users')) or [{}])[0].get('customData')
    except OperationFailure:
        return None
