# -*- coding: utf-8 -*-
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.errors import PyMongoError


MONGO_KEYS = {'host': 'MONGO_HOST', 'port': 'MONGO_PORT'}
ADMIN_KEYS = {'user': 'MONGO_ADMIN', 'pass': 'MONGO_ADMIN_PASS'}


def get_client(app):
    return MongoClient(**{
        param: app.config[key]
        for param, key in MONGO_KEYS.iteritems()
        if key in app.config
    })


@contextmanager
def admin(app, client=None, logout=True):
    client = client or get_client(app)
    client.admin.authenticate(*[
        app.config[key]
        for key in ADMIN_KEYS.values()
    ])
    yield client
    if logout:
        client.admin.logout()
