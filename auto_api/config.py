# -*- coding: utf-8 -*-
import logging

from flask_cors import CORS
from pymongo import MongoClient

from .mongodb import admin, ADMIN_KEYS


AUTH_KEY = 'AUTOAPI_AUTH'


def autoapi_config(app):
    # loggin
    _config_logging(app)

    # cross domain
    CORS(app, resources={r'/*': {'origins': '*'}})

    # config file
    _read_config(app)

    # admin user
    if app.config[AUTH_KEY]:
        _config_admin_user(app)


def _config_logging(app):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARN)
    app.logger.addHandler(stream_handler)


def _read_config(app):
    try:
        app.config.from_envvar('AUTOAPI_SETTINGS')
    except IOError:
        pass
    # both keys must exist for auth
    app.config[AUTH_KEY] = all(key in app.config for key in ADMIN_KEYS.values())
    # TODO: 1 key -> exception, autoapi requiered both !


def _config_admin_user(app):
    with admin(app) as client:
        # TODO: check if an admin exists in order to not run this
        try:
            client.admin.add_user(
                *[app.config[key] for key in ADMIN_KEYS.values()],
                roles=[
                    {'role': 'userAdminAnyDatabase', 'db': 'admin'}
                ],
                customData={
                    'roles': ['admin']
                }
            )
        except:
            pass
        with admin(app, client=client) as client:
            client.admin.command(
                'grantRolesToUser',
                app.config[ADMIN_KEYS['user']],
                roles=['readWriteAnyDatabase']
            )
