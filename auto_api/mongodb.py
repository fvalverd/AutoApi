# -*- coding: utf-8 -*-
from contextlib import contextmanager
import uuid

import OpenSSL
from pymongo import MongoClient
from pymongo.errors import PyMongoError, OperationFailure

from .exceptions import Message
from .messages import unauthenticated


BUILT_IN_ROLES = ['read', 'update', 'create', 'delete', 'admin']
DEFAULT_ROLES = ['read']

MONGO_KEYS = {'host': 'MONGO_HOST', 'port': 'MONGO_PORT'}
ADMIN_KEYS = {'name': 'MONGO_ADMIN', 'password': 'MONGO_ADMIN_PASS'}


def get_values(config, data):
    return {k: config[v] for k, v in data.iteritems() if v in config}


def get_client(app):
    return MongoClient(**get_values(app.config, MONGO_KEYS))


@contextmanager
def admin(app, client=None):
    _client = client or get_client(app)
    try:
        _client.admin.authenticate(**get_values(app.config, ADMIN_KEYS))
    except PyMongoError:
        pass
    yield _client
    if client is None:
        _client.admin.logout()


def _is_original_admin(app, user):
    return user == app.config[ADMIN_KEYS['name']]


def get_info(app, api, client, user):
    db = 'admin' if _is_original_admin(app, user) else api
    result = client[api].command('usersInfo', {'user': user, 'db': db})
    return ((result and result.get('users')) or [{}])[0].get('customData')


def add_user(client, api, user, password, roles):
    client[api].add_user(
        user, password, customData={'roles': roles or DEFAULT_ROLES}
    )


def _create_token():
    return str(uuid.UUID(bytes=OpenSSL.rand.bytes(16)))


def update_roles(app, api, client, user, roles):
    info = get_info(app, api, client, user)
    if info is not None:
        info['roles'] = [
            role
            for role in (info.get('roles') or []) + roles.keys()
            if roles.get(role, True) and role in BUILT_IN_ROLES
        ]
        client[api].command('updateUser', user, customData=info)
        return True


def get_token(app, api, client, user, password):
    api = 'admin' if app.config[ADMIN_KEYS['name']] == user else api
    try:
        client[api].authenticate(user, password)
        client[api].logout()
    except PyMongoError:
        raise Message(unauthenticated())
    token = _create_token()
    with admin(app, client=client) as client:
        result = client[api].command('usersInfo', {'user': user, 'db': api})
        customData = result.get('users')[0].get('customData')
        customData['tokens'] = customData.get('tokens', []) + [token]
        client[api].command('updateUser', user, customData=customData)
        return token


def remove_token(app, api, user, token):
    api = 'admin' if app.config[ADMIN_KEYS['name']] == user else api
    with admin(app) as client:
        result = client[api].command('usersInfo', {'user': user, 'db': api})
        customData = result.get('users')[0].get('customData')
        if token in customData.get('tokens', []):
            customData['tokens'].remove(token)
            client[api].command('updateUser', user, customData=customData)
