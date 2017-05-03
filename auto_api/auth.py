# -*- coding: utf-8 -*-
from functools import wraps
import inspect
import json
import uuid

from flask import request
import OpenSSL
from pymongo.errors import OperationFailure, PyMongoError

from .messages import invalid, message, ok_no_data, response, \
    unauthorized, unlogged
from .mongodb import admin, get_client


BUILT_IN_ROLES = ['read', 'update', 'create', 'delete', 'admin']
DEFAULT_ROLES = ['read']


def login(app):
    params = request.json or request.form.to_dict()
    if params.get('email') and params.get('api'):
        token = _login_and_get_token(
            app,
            params['api'],
            email=params['email'],
            password=params.get('password')
        )
        if token is not None:
            return response(
                data={'email': params.get('email'), 'token': token},
                headers={'X-Email': params.get('email'), 'X-Token': token}
            )
    return invalid()


def logout(app):
    params = request.json or request.form.to_dict()
    if _logout_and_remove_token(app, params.get('api')):
        return ok_no_data()
    return invalid()


def user(mongo_client):
    params = request.json
    if params.get('email') and params.get('password') and params.get('api'):
        mongo_client[params.get('api')].add_user(
            params.get('email'),
            params.get('password'),
            customData={
                'roles': params.get('roles') or DEFAULT_ROLES
            }
        )
        return ok_no_data()
    return invalid()


def password(app, mongo_client):
    params = request.json or request.form.to_dict()
    if params.get('password') and params.get('api'):
        _, __, is_admin = _check(app, params.get('api'), 'admin')
        if is_admin or params.get('email') == request.headers['X-Email']:
            mongo_client[params.get('api')].add_user(
                params.get('email'),
                params.get('password')
            )
            return ok_no_data()
    return invalid()


def roles(app, mongo_client):
    params = request.json
    if params.get('email') and params.get('api') and params.get('roles'):
        try:
            result = mongo_client[params.get('api')].command('usersInfo', {
                'user': params.get('email'),
                'db': params.get('api')
            })
        except OperationFailure:
            return invalid()
        else:
            if result.get('users'):
                user = result['users'][0]
                customData = user.get('customData', {})
                roles = customData.get('roles') or []
                customData['roles'] = [
                    role
                    for role in roles + params['roles'].keys()
                    if params['roles'].get(role, True)
                ]
                mongo_client[params.get('api')].command(
                    'updateUser',
                    params.get('email'),
                    customData=customData
                )
                return ok_no_data()
    return invalid()


def secure(app, role=None, api=None, auth=True):
    def wrapper(controller):
        @wraps(controller)
        def wrapped(*args, **kwargs):
            params = request.json or request.form.to_dict()
            _api = api or kwargs.get('api') or params.get('api')
            argspec = inspect.getargspec(controller)[0]
            if 'app' in argspec:
                kwargs['app'] = app
            client, is_logged, is_auth = _check(app, _api, role, auth=auth)
            if is_logged:
                if is_auth:
                    if 'mongo_client' in argspec:
                        kwargs['mongo_client'] = client
                    result = controller(*args, **kwargs)
                    client.close()
                    return result
                return unauthorized(_api)
            return unlogged(_api)
        return wrapped
    return wrapper


def _login_and_get_token(app, api, email, password):
    api = 'admin' if app.config['MONGO_ADMIN'] == email else api
    client = get_client(app)
    try:
        client[api].authenticate(email, password)
        client[api].logout()
    except PyMongoError:
        pass
    else:
        token = _create_token()
        with admin(app, client=client) as client:
            result = client[api].command(
                'usersInfo',
                {'user': email, 'db': api}
            )
            customData = result.get('users')[0].get('customData')
            customData['tokens'] = customData.get('tokens', []) + [token]
            client[api].command('updateUser', email, customData=customData)
            return token


def _logout_and_remove_token(app, api):
    token = request.headers.get('X-Token')
    email = request.headers.get('X-Email')
    api = 'admin' if app.config['MONGO_ADMIN'] == email else api
    with admin(app) as client:
        result = client[api].command(
            'usersInfo',
            {'user': email, 'db': api}
        )
        customData = result.get('users')[0].get('customData')
        if token in customData.get('tokens', []):
            customData['tokens'].remove(token)
            client[api].command(
                'updateUser',
                request.headers.get('X-Email'),
                customData=customData
            )
            return True


def _create_token():
    return str(uuid.UUID(bytes=OpenSSL.rand.bytes(16)))


def _is_original_admin(app):
    return request.headers.get('X-Email') == app.config['MONGO_ADMIN']


def _check(app, api, role, auth=True):
    client = get_client(app)
    if not auth:
        return client, True, True
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        with admin(app, client=client, logout=False) as admin_client:
            try:
                result = admin_client[api].command('usersInfo', {
                    'user': request.headers['X-Email'],
                    'db': 'admin' if _is_original_admin(app) else api
                })
            except OperationFailure:
                pass
            user = (result.get('users') or [{}])[0]
            if user.get('customData', {}).get('tokens'):
                request_token = request.headers.get('X-Token')
                user_db_tokens = user['customData']['tokens']
                roles = user.get('customData', {}).get('roles') or []
                return (
                    admin_client,
                    request_token in user_db_tokens,
                    role is None or 'admin' in roles or role in roles
                )
    return None, False, False
