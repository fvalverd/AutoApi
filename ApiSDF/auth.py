# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import wraps
import inspect
import json
import uuid

from flask import jsonify, request, Response
import OpenSSL
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError


BUILT_IN_ROLES = ['read', 'update', 'create', 'delete', 'admin']
DEFAULT_ROLES = ['read']


def login(app):
    params = request.json or request.form.to_dict()
    if params.get('email') and params.get('api'):
        token = _login_and_get_token(
            app,
            params.get('api'),
            email=params.get('email'),
            password=params.get('password')
        )
        if token is not None:
            return Response(
                response=json.dumps({
                    'email': params.get('email'),
                    'token': token
                }),
                headers={
                    'X-Email': params.get('email'),
                    'X-Token': token
                },
                mimetype="application/json"
            )
    return _invalid_data()


def logout(app):
    params = request.json or request.form.to_dict()
    if _logout_and_remove_token(app, params.get('api')):
        return Response(status=204)
    return _invalid_data()


def create_user(mongo_client):
    params = request.json
    if params.get('email') and params.get('password') and params.get('api'):
        mongo_client[params.get('api')].add_user(
            params.get('email'),
            params.get('password'),
            customData={
                'roles': params.get('roles') or DEFAULT_ROLES
            }
        )
        return Response(status=201)
    return _invalid_data()


def add_app(app, controller):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, app=app, **kwargs)
        return wrapped
    return wrapper(controller)


def secure(app, controller, role=None):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            params = request.json or request.form.to_dict()
            api = kwargs.get('api') or params.get('api')
            argspec = inspect.getargspec(func)[0]
            if 'app' in argspec:
                kwargs['app'] = app
            client, is_authorized = _is_authorized(app, api, role)
            if is_authorized:
                if 'mongo_client' in argspec:
                    kwargs['mongo_client'] = client
                result = func(*args, **kwargs)
                client.close()
                return result
            return _not_logged(api)
        return wrapped
    return wrapper(controller)


def _not_logged(api):
    return Response(
        status=401,
        response=json.dumps({
            'message': u'You must be logged in "%s" api' % api
        }),
        mimetype="application/json"
    )


def _invalid_data():
    return Response(
        status=400,
        response=json.dumps({'message': u'Invalid email/password/api'}),
        mimetype="application/json"
    )


def _login_and_get_token(app, api, email, password):
    client = _get_mongo_client(app)
    try:
        client[api].authenticate(email, password)
        client[api].logout()
    except PyMongoError:
        pass
    else:
        token = _create_token()
        with _admin_manager_client(app, client=client) as client:
            result = client[api].command(
                'usersInfo',
                {'user': email, 'db': api}
            )
            customData = result.get('users')[0].get('customData')
            customData['token'] = token
            client[api].command('updateUser', email, customData=customData)
            return token


def _logout_and_remove_token(app, api):
    with _admin_manager_client(app) as client:
        result = client[api].command(
            'usersInfo',
            {'user': request.headers.get('X-Email'), 'db': api}
        )
        customData = result.get('users')[0].get('customData')
        if request.headers.get('X-Token') == customData['token']:
            del customData['token']
            client[api].command(
                'updateUser',
                request.headers.get('X-Email'),
                customData=customData
            )
            return True


def _create_token():
    return str(uuid.UUID(
        bytes=OpenSSL.rand.bytes(16)
    ))


def _get_mongo_client(app):
    return MongoClient(
        host=app.config['MONGO_HOST'],
        port=app.config['MONGO_PORT']
    )


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


def _is_original_admin(app):
    return request.headers.get('X-Email') == app.config['MONGO_ADMIN']


def _is_authorized(app, api, role):
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        with _admin_manager_client(app, logout=False) as client:
            try:
                result = client[api].command('usersInfo', {
                    'user': request.headers['X-Email'],
                    'db': 'admin' if _is_original_admin(app) else api
                })
            except OperationFailure:
                pass
            user = (result.get('users') or [{}])[0]
            if user.get('customData', {}).get('token'):
                request_token = request.headers.get('X-Token')
                user_db_token = user['customData']['token']
                if request_token == user_db_token:
                    roles = user.get('customData', {}).get('roles') or []
                    roles.append(None)  # without restriction
                    return client, 'admin' in roles or role in roles
    return None, False
