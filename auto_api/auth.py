# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import wraps
import inspect
import sys

from flask import request

from .exceptions import Message
from .messages import bad_request, unauthorized, unlogged
from .mongodb import admin, get_custom_data
from .validations import validate_api


def _get_arguments(view):
    if sys.version_info >= (3, 4):
        return inspect.signature(view).parameters
    return inspect.getargspec(view).args


def _d(api, app, client, view, kwargs):
    arguments = _get_arguments(view)
    if 'api' in arguments:
        kwargs['api'] = api
    if 'app' in arguments:
        kwargs['app'] = app
    if 'client' in arguments:
        kwargs['client'] = client
    return kwargs


def _check_auth(api, authenticated, authorized):
    if not authenticated:
        raise Message(unlogged(api))
    elif not authorized:
        raise Message(unauthorized(api))


def _get_api(no_api=False):
    params = request.json or request.form.to_dict()
    api = params.get('api')
    if api is not None or no_api:
        return api
    raise Message(bad_request(u'Missing "api" parameter'))


def secure(app, view, role=None, api=None, auth=False, no_api=False):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            _api = api or kwargs.get('api') or _get_api(no_api=no_api)
            _api = validate_api(_api)
            with check(app, _api, role, auth) as (authenticated, authorized):
                _check_auth(_api, authenticated, authorized)
                with admin(app) as client:
                    value = view(*args, **_d(_api, app, client, view, kwargs))
                return value
        except Message as m:
            return m.message
    return wrapper


@contextmanager
def check(app, api, role, auth=True):
    authenticated, authorized = not auth, not auth
    if auth and 'X-Email' in request.headers and 'X-Token' in request.headers:
        email, token = request.headers['X-Email'], request.headers['X-Token']
        with admin(app) as client:
            info, _ = get_custom_data(app, api, client, email)
            if info is not None and info.get('tokens'):
                roles = info.get('roles') or []
                authenticated = token in info['tokens']
                authorized = role is None or 'admin' in roles or role in roles
    yield (authenticated, authorized)
