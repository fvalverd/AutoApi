# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import wraps
import inspect

from flask import request

from .messages import bad_request, forbidden, ok_no_data, response, \
    unauthenticated, unauthorized, unlogged
from .mongodb import add_user, admin, get_client, get_info, \
    login_and_get_token, logout_and_remove_token, update_roles
from .utils import get_api_from_params


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
        api, user, password = params['api'], params['email'], params['password']
        add_user(mongo_client, api, user, password, params.get('roles'))
        return ok_no_data()
    return bad_request(u"Missing parameters")


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
        if update_roles(
            app, params['api'], mongo_client, params['email'], params['roles']
        ):
            return ok_no_data()
        return forbidden(u"User does not exists")
    return bad_request(u"Missing parameters")


def inject(app, client, controller, kwargs):
    argspec = inspect.getargspec(controller)[0]
    if 'app' in argspec:
        kwargs['app'] = app
    if 'mongo_client' in argspec:
        kwargs['mongo_client'] = client
    return kwargs


def secure(app, role=None, api=None, auth=False):
    def wrapper(controller):
        @wraps(controller)
        def wrapped(*args, **kw):
            _api = api or kw.get('api') or get_api_from_params(request)
            with check(app, _api, role, auth) as (client, logged, authorized):
                if not logged:
                    return unlogged(_api)
                elif not authorized:
                    return unauthorized(_api)
                return controller(*args, **inject(app, client, controller, kw))
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
