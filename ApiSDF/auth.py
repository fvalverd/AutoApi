# -*- coding: utf-8 -*-
from contextlib import contextmanager
import json
from functools import wraps
import uuid

from flask import jsonify, request
import OpenSSL
from pymongo import MongoClient


def secure(app, *roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            db, is_authorized = _is_authorized_token_and_get_db(app)
            if is_authorized:
                kwargs['db'] = db
                func_return = func(*args, **kwargs)
                db.connection.close()
                return func_return
            return jsonify({'message': u'You must be logged'}), 401
        return wrapped
    return wrapper


def login_and_get_token(app, email, password):
    db = _get_mongo(app)
    if db.authenticate(email, password):
        return _create_and_save_token(app, email, db=db)


def logout_and_remove_token(app, db):
    if request.headers.get('X-Email') and request.headers.get('X-Token'):
        return _remove_token(
            app,
            db,
            email=request.headers.get('X-Email'),
            token=request.headers.get('X-Token')
        )
    return False


def _get_mongo(app):
    client = MongoClient(
        host=app.config['MONGO_HOST'],
        port=app.config['MONGO_PORT']
    )
    return client[app.config['APISDF_DB']]


@contextmanager
def _admin_manager(app, db=None, logout=True):
    db = db or _get_mongo(app)
    db.authenticate(
        app.config['APISDF_ADMIN'],
        app.config['APISDF_ADMIN_PASS']
    )
    yield db
    if logout:
        db.logout()


def _is_authorized_token_and_get_db(app):
    with _admin_manager(app, logout=False) as db:
        if request.headers.get('X-Email') and request.headers.get('X-Token'):
            result = db.command(
                'usersInfo',
                {
                    'user': request.headers['X-Email'],
                    'db': app.config['APISDF_DB']
                }
            )
            if result.get('users', [{}])[0].get('customData', {}).get('token'):
                request_token = request.headers.get('X-Token')
                user_db_token = result['users'][0]['customData']['token']
                return db, request_token == user_db_token
    return None, False


def _create_and_save_token(app, email, db=None):
    token = str(uuid.UUID(bytes=OpenSSL.rand.bytes(16)))
    with _admin_manager(app, db=db) as db:
        db.command('updateUser', email, customData={'token': token})
    return token


def _remove_token(app, db, email, token):
    with _admin_manager(app, db=db) as db:
        result = db.command('updateUser', email, customData={})
        return result is not None and result.get('ok') == 1.0
    return False
