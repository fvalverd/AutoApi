# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import wraps
import inspect

from flask import request
from pymongo.errors import OperationFailure

from .messages import ok_no_data, response, unauthenticated, \
    unauthorized, unlogged
from .mongodb import admin, get_client, get_info, \
    login_and_get_token, logout_and_remove_token
from .utils import get_api_from_params


BUILT_IN_ROLES = ['read', 'update', 'create', 'delete', 'admin']
DEFAULT_ROLES = ['read']


def login(app):
    params = request.json or request.form.to_dict()
    if params.get('email') and params.get('api') and params.get('password'):
        api, user, password = params['api'], params['email'], params['password']
        token = login_and_get_token(app, api, user, password)
        if token is not None:
            return response(
                data={'email': user, 'token': token},
                headers={'X-Email': user, 'X-Token': token}
            )
    return unauthenticated()


def logout(app):
    params = request.json or request.form.to_dict()
    user = request.headers.get('X-Email')
    token = request.headers.get('X-Token')
    if logout_and_remove_token(app, params.get('api'), user, token):
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


@contextmanager
def check(app, api, role, auth=False):
    client, authenticated, authorized = get_client(app), not auth, not auth
    if auth and 'X-Email' in request.headers and 'X-Token' in request.headers:
        with admin(app, client=client, logout=False) as client:
            info = get_info(app, api, client, request.headers['X-Email'])
            if info is not None and info.get('tokens'):
                roles = info.get('roles') or []
                authenticated = request.headers['X-Token'] in info['tokens']
                authorized = role is None or 'admin' in roles or role in roles
    yield (client, authenticated, authorized)
    client.close()
