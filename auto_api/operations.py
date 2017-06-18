# -*- coding: utf-8 -*-
from flask import request

from .auth import check
from .messages import bad_request, forbidden, ok, response
from .mongodb import add_user, get_token, remove_token, update_roles
from .validations import validate_api


def invalid_operation(api):
    return bad_request(u'This is not a valid operation')


def _get_params():
    params = request.json or request.form.to_dict()
    if 'api' in params:
        params['api'] = validate_api(params['api'])
    return params


def login(app, client):
    params = _get_params()
    if params.get('email') and params.get('api') and params.get('password'):
        api, user, _pass = params['api'], params['email'], params['password']
        token = get_token(app, api, client, user, _pass)
        return response(
            data={'email': user, 'token': token},
            headers={'X-Email': user, 'X-Token': token}
        )
    return bad_request(u"Missing parameters")


def logout(app):
    params = _get_params()
    user, token = [request.headers.get(key) for key in ('X-Email', 'X-Token')]
    remove_token(app, params['api'], user, token)
    return ok()


def user(client):
    params = _get_params()
    if params.get('email') and params.get('password') and params.get('api'):
        api, user, _pass = params['api'], params['email'], params['password']
        add_user(client, api, user, _pass, params.get('roles'))
        return ok()
    return bad_request(u"Missing parameters")


def password(app, client):
    params = _get_params()
    if params.get('api') and params.get('email') and params.get('password'):
        with check(app, params['api'], 'admin', quiet=True) as (_, _admin, __):
            user, password = params['email'], params['password']
            if _admin or user == request.headers['X-Email']:
                client[params['api']].add_user(user, password)
                return ok()
    return bad_request(u"Missing parameters")


def roles(app, client):
    params = _get_params()
    if params.get('email') and params.get('api') and params.get('roles'):
        if update_roles(
            app, params['api'], client, params['email'], params['roles']
        ):
            return ok()
        return forbidden(u"User does not exists")
    return bad_request(u"Missing parameters")
