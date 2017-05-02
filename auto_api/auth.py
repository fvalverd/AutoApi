# -*- coding: utf-8 -*-
from functools import wraps
import inspect
import json
import uuid

from flask import jsonify, request, Response
import OpenSSL
from pymongo.errors import OperationFailure, PyMongoError

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
        return Response(status=204)
    return _invalid_data()


def password(app, mongo_client):
    params = request.json or request.form.to_dict()
    if params.get('password') and params.get('api'):
        _, __, is_admin = _check(app, params.get('api'), 'admin')
        if is_admin or params.get('email') == request.headers['X-Email']:
            mongo_client[params.get('api')].add_user(
                params.get('email'),
                params.get('password')
            )
            return Response(status=204)
    return _invalid_data()


def roles(app, mongo_client):
    params = request.json
    if params.get('email') and params.get('api') and params.get('roles'):
        try:
            result = mongo_client[params.get('api')].command('usersInfo', {
                'user': params.get('email'),
                'db': params.get('api')
            })
        except OperationFailure:
            return _invalid_data()
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
                return Response(status=204)
    return _invalid_data()


def add_app(app, controller):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, app=app, **kwargs)
        return wrapped
    return wrapper(controller)


def secure(app, controller, role=None, api=None):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            params = request.json or request.form.to_dict()
            _api = api or kwargs.get('api') or params.get('api')
            argspec = inspect.getargspec(func)[0]
            if 'app' in argspec:
                kwargs['app'] = app
            client, is_authenticated, is_authorized = _check(app, _api, role)
            if is_authenticated:
                if is_authorized:
                    if 'mongo_client' in argspec:
                        kwargs['mongo_client'] = client
                    result = func(*args, **kwargs)
                    client.close()
                    return result
                return _not_authorized(_api)
            return _not_logged(_api)
        return wrapped
    return wrapper(controller)


def _not_authorized(api):
    return Response(
        status=403,
        response=json.dumps({
            'message': u'You must be authorized in "%s" api' % api
        }),
        mimetype="application/json"
    )


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


def _check(app, api, role):
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        with admin(app, logout=False) as client:
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
                return (
                    client,
                    request_token in user_db_tokens,
                    role is None or 'admin' in roles or role in roles
                )
    return None, False, False
