# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import wraps
import inspect
import uuid

from flask import request
import OpenSSL
from pymongo.errors import OperationFailure, PyMongoError

from .messages import ok_no_data, response, unauthenticated, \
    unauthorized, unlogged
from .mongodb import admin, ADMIN_KEYS, get_client
from .utils import get_api_from_params


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
    return unauthenticated()


def logout(app):
    params = request.json or request.form.to_dict()
    if _logout_and_remove_token(app, params.get('api')):
        return ok_no_data()
    return unauthenticated()


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
    return unauthenticated()


def password(app, mongo_client):
    params = request.json or request.form.to_dict()
    api, email, password = (
        params.get('api'), params.get('email'), params.get('password')
    )
    if password and api:
        with check(app, api, 'admin', auth=True) as (_, __, admin):
            if admin or email == request.headers['X-Email']:
                mongo_client[api].add_user(email, password)
                return ok_no_data()
    return unauthenticated()


def roles(app, mongo_client):
    params = request.json
    if params.get('email') and params.get('api') and params.get('roles'):
        try:
            result = mongo_client[params.get('api')].command('usersInfo', {
                'user': params.get('email'),
                'db': params.get('api')
            })
        except OperationFailure:
            return unauthenticated()
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
    return unauthenticated()


def secure(app, role=None, api=None, auth=False):
    def wrapper(controller):
        @wraps(controller)
        def wrapped(*args, **kwargs):
            _api = api or kwargs.get('api') or get_api_from_params(request)

            # Check authentication and authorization
            with check(app, _api, role, auth) as (client, logged, authorized):
                # Return error messages
                if not logged:
                    return unlogged(_api)
                if not authorized:
                    return unauthorized(_api)

                # Inject requested parameters
                argspec = inspect.getargspec(controller)[0]
                if 'app' in argspec:
                    kwargs['app'] = app
                if 'mongo_client' in argspec:
                    kwargs['mongo_client'] = client

                # Apply original controller
                return controller(*args, **kwargs)
        return wrapped
    return wrapper


# TODO: next functions are utils

def _login_and_get_token(app, api, email, password):
    api = 'admin' if app.config[ADMIN_KEYS['name']] == email else api
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
    api = 'admin' if app.config[ADMIN_KEYS['name']] == email else api
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
    return request.headers.get('X-Email') == app.config[ADMIN_KEYS['name']]


@contextmanager
def check(app, api, role, auth=False):
    client = get_client(app)
    if not auth:
        yield (client, True, True)
    elif request.headers.get('X-Email') and request.headers.get('X-Token'):
        with admin(app, client=client, logout=False) as client:
            try:
                result = client[api].command('usersInfo', {
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
                yield (
                    client,
                    request_token in user_db_tokens,
                    role is None or 'admin' in roles or role in roles
                )
            else:
                yield (None, False, False)
    else:
        yield (None, False, False)
    client.close()
