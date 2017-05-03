# -*- coding: utf-8 -*-
import logging

from flask_cors import CORS
from pymongo import MongoClient

from .exceptions import AutoApiMissingAdminConfig
from .mongodb import admin, ADMIN_KEYS


AUTOAPI_SETTINGS_VAR = 'AUTOAPI_SETTINGS'


def config(autoapi, cors=True, logging_level=logging.WARN, path=None):
    # loggin
    _config_logging(autoapi, level=logging_level)

    # cross domain
    if cors:
        CORS(autoapi.app, resources={r'/*': {'origins': '*'}})

    # config file
    _read_config(autoapi, path)

    # admin user
    if autoapi.auth:
        _config_admin_user(autoapi)


def _config_logging(autoapi, level):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    autoapi.app.logger.addHandler(stream_handler)


def _read_config(autoapi, path):
    if path is not None:
        autoapi.app.config.from_pyfile(path)
    else:
        try:
            autoapi.app.config.from_envvar(AUTOAPI_SETTINGS_VAR)
        except RuntimeError:
            pass  # Ignore if AUTOAPI_SETTINGS is not setted

    if autoapi.auth and any(key not in autoapi.app.config for key in ADMIN_KEYS.values()):
        raise AutoApiMissingAdminConfig('Check your configuration !')


def _config_admin_user(autoapi):
    with admin(autoapi.app) as client:
        # admin for all databases
        # TODO: check if an admin exists in order to not run this
        client.admin.add_user(
            *[autoapi.app.config[key] for key in ADMIN_KEYS.values()],
            roles=[
                {'role': 'userAdminAnyDatabase', 'db': 'admin'}
            ],
            customData={
                'roles': ['admin']
            }
        )

        # admin read & write
        client.admin.command(
            'grantRolesToUser',
            autoapi.app.config[ADMIN_KEYS['user']],
            roles=['readWriteAnyDatabase']
        )
