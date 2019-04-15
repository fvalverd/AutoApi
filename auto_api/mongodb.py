# -*- coding: utf-8 -*-
from contextlib import contextmanager
import uuid

from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError

from .exceptions import Message
from .messages import unauthenticated


BUILT_IN_ROLES = ['read', 'update', 'create', 'delete', 'admin']
DEFAULT_ROLES = ['read']

MONGO_KEYS = {'host': 'MONGO_HOST', 'port': 'MONGO_PORT'}
ADMIN_KEYS = {'name': 'MONGO_ADMIN', 'password': 'MONGO_ADMIN_PASS'}


def get_values(config, data):
    return {k: config[v] for k, v in data.items() if v in config}


def get_client(app):
    return MongoClient(**get_values(app.config, MONGO_KEYS))


@contextmanager
def admin(app):
    client = get_client(app)
    try:
        client.admin.authenticate(**get_values(app.config, ADMIN_KEYS))
    except PyMongoError:
        pass
    yield client
    client.close()


def _is_original_admin(app, user):
    return user == app.config[ADMIN_KEYS['name']]


def get_custom_data(app, api, client, user):
    db = 'admin' if _is_original_admin(app, user) else api
    result = client[api].command('usersInfo', {'user': user, 'db': db})
    return ((result and result.get('users')) or [{}])[0].get('customData'), db


def create_user(app, api, user, password, roles=None, db_roles=None):
    with admin(app) as client:
        try:
            client[api].command(
                'createUser',
                user,
                pwd=password,
                roles=db_roles or [],
                customData={'roles': roles or DEFAULT_ROLES},
            )
        except DuplicateKeyError:
            return False
    return True


def update_user_password(app, api, user, password):
    with admin(app) as client:
        client[api].command('updateUser', user, pwd=password)


def _create_token():
    return str(uuid.uuid4())


def update_roles(app, api, user, roles):
    with admin(app) as client:
        data, db = get_custom_data(app, api, client, user)
        if data is not None:
            data['roles'] = [
                role
                for role in (data.get('roles') or []) + list(roles.keys())
                if roles.get(role, True) and role in BUILT_IN_ROLES
            ]
            client[db].command('updateUser', user, customData=data)
            return True
    return False


def create_token(app, api, user, password):
    try:
        db = 'admin' if _is_original_admin(app, user) else api
        client = get_client(app)
        client[db].authenticate(user, password)
    except PyMongoError:
        raise Message(unauthenticated())
    finally:
        client.close()
    token = _create_token()
    with admin(app) as client:
        data, db = get_custom_data(app, api, client, user)
        data['tokens'] = data.get('tokens', []) + [token]
        client[db].command('updateUser', user, customData=data)
        return token


def delete_token(app, api, user, token):
    with admin(app) as client:
        data, db = get_custom_data(app, api, client, user)
        if token in data.get('tokens', []):
            data['tokens'].remove(token)
            client[db].command('updateUser', user, customData=data)
