# -*- coding: utf-8 -*-
from contextlib import contextmanager
import json
from functools import wraps
import uuid

from flask import jsonify, request
import OpenSSL
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError


def secure(app, role=None, logout=False, api=None):
    def wrapper(func):
        _api = api

        @wraps(func)
        def wrapped(*args, **kwargs):
            api = _api
            if api is None:
                if logout:
                    params = request.json or request.form.to_dict()
                    api = params.get('api')
                else:
                    api = kwargs.get('api')
            client, is_authorized = _is_authorized_token_and_get_client(app, api)
            if is_authorized:
                func_return = func(*args, mongo_client=client, **kwargs)
                client.close()
                return func_return
            return (
                jsonify({'message': u'You must be logged in "%s" api' % api}),
                401
            )
        return wrapped
    return wrapper


def login_and_get_token(app, api, email, password):
    client = _get_mongo_client(app)
    try:
        client[api].authenticate(email, password)
        client[api].logout()
    except PyMongoError:
        pass
    else:
        token = _create_token()
        with _admin_manager_client(app, client=client) as client:
            client[api].command('updateUser', email, customData={'token': token})
            return token


def logout_and_remove_token(app, api):
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        with _admin_manager_client(app) as client:
            client[api].command(
                'updateUser',
                request.headers.get('X-Email'),
                customData={}
            )
            return True


def _create_token():
    return str(uuid.UUID(bytes=OpenSSL.rand.bytes(16)))


def _get_mongo_client(app):
    return MongoClient(host=app.config['MONGO_HOST'], port=app.config['MONGO_PORT'])


@contextmanager
def _admin_manager_client(app, client=None, logout=True):
    client = client or _get_mongo_client(app)
    try:
        client.admin.authenticate(
            app.config['MONGO_ADMIN'],
            app.config['MONGO_ADMIN_PASS']
        )
    except PyMongoError:
        pass
    yield client
    if logout:
        client.admin.logout()


def _is_authorized_token_and_get_client(app, api):
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        with _admin_manager_client(app, logout=False) as client:
            try:
                result = client[api].command(
                    'usersInfo',
                    {'user': request.headers['X-Email'], 'db': api}
                )
            except OperationFailure:
                pass
            else:
                user = (result.get('users') or [{}])[0]
                if user.get('customData', {}).get('token'):
                    request_token = request.headers.get('X-Token')
                    user_db_token = user['customData']['token']
                    return client, request_token == user_db_token
    return None, False
