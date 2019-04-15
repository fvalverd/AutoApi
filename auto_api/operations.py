# -*- coding: utf-8 -*-
from flask import request

from .auth import check
from .messages import bad_request, forbidden, invalid, ok, response
from .mongodb import create_user, create_token, delete_token, update_roles, \
    update_user_password
from .validations import validate_api
from .utils import _pluck


def invalid_operation(api):
    return bad_request(u'This is not a valid operation')


def _params(*keys):
    data = request.json or request.form.to_dict()
    data['api'] = validate_api(data.get('api'))
    return _pluck(data, *keys)


def _headers(*keys):
    return _pluck(request.headers, *keys)


def login(app):
    api, user, password = _params('api', 'email', 'password')
    if api and user and password:
        token = create_token(app, api, user, password)
        return response(
            data={'email': user, 'token': token},
            headers={'X-Email': user, 'X-Token': token}
        )
    return bad_request(u'Missing parameters')


def logout(app):
    api = _params('api')
    user, token = _headers('X-Email', 'X-Token')
    delete_token(app, api, user, token)
    return ok()


def user(app):
    api, user, password, roles = _params('api', 'email', 'password', 'roles')
    if api and user and password:
        if create_user(app, api, user, password, roles):
            return ok()
        return invalid(u'User already exists')
    return bad_request(u'Missing parameters')


def password(app):
    api, user, password = _params('api', 'email', 'password')
    if api and user and password:
        with check(app, api, 'admin') as (_, is_admin):
            if is_admin or user == _headers('X-Email'):
                update_user_password(app, api, user, password)
                return ok()
            return invalid(u'A user can only change their own password')
    return bad_request(u'Missing parameters')


def roles(app):
    api, user, roles = _params('api', 'email', 'roles')
    if api and user and roles:
        if update_roles(app, api, user, roles):
            return ok()
        return forbidden(u'User does not exists')
    return bad_request(u'Missing parameters')
