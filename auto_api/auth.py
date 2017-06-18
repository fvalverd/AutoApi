# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import wraps
import inspect

from flask import request

from .exceptions import Message
from .messages import unauthorized, unlogged
from .mongodb import admin, get_client, get_info
from .utils import get_api
from .validations import validate_api


def _inject(api, app, client, view, kwargs):
    argspec = inspect.getargspec(view)[0]
    if 'api' in argspec:
        kwargs['api'] = api
    if 'app' in argspec:
        kwargs['app'] = app
    if 'client' in argspec:
        kwargs['client'] = client
    return kwargs


def secure(app, view, role=None, api=None, auth=False, without_api=False):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            _api = api or kwargs.get('api') or get_api(without_api=without_api)
            _api = validate_api(_api)
            with check(app, _api, role, auth) as (client, _, __):
                return view(*args, **_inject(_api, app, client, view, kwargs))
        except Message as m:
            return m.message
    return wrapper


def _check_auth(quiet, api, authenticated, authorized):
    if not quiet:
        if not authenticated:
            raise Message(unlogged(api))
        elif not authorized:
            raise Message(unauthorized(api))


@contextmanager
def check(app, api, role, auth=True, quiet=False):
    client, authenticated, authorized = get_client(app), not auth, not auth
    if auth and 'X-Email' in request.headers and 'X-Token' in request.headers:
        with admin(app, client=client) as client:
            info = get_info(app, api, client, request.headers['X-Email'])
            if info is not None and info.get('tokens'):
                roles = info.get('roles') or []
                authenticated = request.headers['X-Token'] in info['tokens']
                authorized = role is None or 'admin' in roles or role in roles
    _check_auth(quiet, api, authenticated, authorized)
    yield (client, authenticated, authorized)
    client.close()
