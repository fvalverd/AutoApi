# -*- coding: utf-8 -*-
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.errors import PyMongoError


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
