# -*- coding: utf-8 -*-
from contextlib import contextmanager
import json
from functools import wraps
import uuid

from flask import jsonify, request
import OpenSSL
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError


def secure(app, role=None, logout=False):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if logout:
                params = request.json or request.form.to_dict()
                api = params.get('api')
            else:
                api = kwargs.get('api')
            db, is_authorized = _is_authorized_token_and_get_db(app, api)
            if is_authorized:
                func_return = func(*args, db=db, **kwargs)
                db.connection.close()
                return func_return
            return (
                jsonify({'message': u'You must be logged in "%s" api' % api}),
                401
            )
        return wrapped
    return wrapper


def login_and_get_token(app, api, email, password):
    db = _get_mongo(app, api)
    try:
        db.authenticate(email, password)
    except PyMongoError:
        pass
    else:
        token = _create_token()
        with _admin_manager(app, api, db=db) as db:
            db.command('updateUser', email, customData={'token': token})
            return token


def logout_and_remove_token(app, api, db):
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        with _admin_manager(app, api, db=db) as db:
            db.command(
                'updateUser',
                request.headers.get('X-Email'),
                customData={}
            )
            return True


def _create_token():
    return str(uuid.UUID(bytes=OpenSSL.rand.bytes(16)))


def _get_mongo(app, api):
    client = MongoClient(
        host=app.config['MONGO_HOST'],
        port=app.config['MONGO_PORT']
    )
    return client[api]


@contextmanager
def _admin_manager(app, api, db=None, logout=True):
    db = db or _get_mongo(app, api)
    try:
        db.authenticate(
            app.config['APISDF_ADMIN'],
            app.config['APISDF_ADMIN_PASS']
        )
    except PyMongoError:
        yield db
    else:
        yield db
        if logout:
            db.logout()


def _is_authorized_token_and_get_db(app, api):
    with _admin_manager(app, api, logout=False) as db:
        if request.headers.get('X-Email') and request.headers.get('X-Token'):
            try:
                result = db.command(
                    'usersInfo',
                    {'user': request.headers['X-Email'], 'db': api}
                )
            except OperationFailure:
                pass
            else:
                if result.get('users', [{}])[0].get('customData', {}).get('token'):
                    request_token = request.headers.get('X-Token')
                    user_db_token = result['users'][0]['customData']['token']
                    return db, request_token == user_db_token
    return None, False
