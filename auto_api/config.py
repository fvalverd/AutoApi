# -*- coding: utf-8 -*-
import logging

from flask_cors import CORS

from .exceptions import AutoApiMissingAdminConfig
from .mongodb import admin, get_values, ADMIN_KEYS, MONGO_KEYS


AUTOAPI_SETTINGS_VAR = 'AUTOAPI_SETTINGS'


def config_autoapi(
    autoapi, cors=True, logging_level=logging.WARN,
    path=None, force_port=None
):
    _config_logging(autoapi, level=logging_level)
    if cors:
        CORS(autoapi.app, resources={r'/*': {'origins': '*'}})
    _read_config(autoapi, path, force_port=force_port)
    if autoapi.auth:
        _config_admin_user(autoapi)


def _config_logging(autoapi, level):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    autoapi.app.logger.addHandler(stream_handler)


def _read_config(autoapi, path, force_port=None):
    if path is not None:
        autoapi.app.config.from_pyfile(path)
    else:
        try:
            autoapi.app.config.from_envvar(AUTOAPI_SETTINGS_VAR)
        except RuntimeError:
            pass  # Ignore if AUTOAPI_SETTINGS is not setted

    if force_port is not None:
        autoapi.app.config[MONGO_KEYS['port']] = force_port

    if autoapi.auth and any(
        key not in autoapi.app.config for key in ADMIN_KEYS.values()
    ):
        raise AutoApiMissingAdminConfig('Check your configuration !')


def _config_admin_user(autoapi):
    with admin(autoapi.app) as client:
        # Ensure that admin user exists
        client.admin.add_user(
            roles=[{'role': 'userAdminAnyDatabase', 'db': 'admin'}],
            customData={'roles': ['admin']},
            **get_values(autoapi.app.config, ADMIN_KEYS)
        )

        # Ensure that admin has privileges
        with admin(autoapi.app, client=client) as client:
            client.admin.command(
                'grantRolesToUser',
                autoapi.app.config[ADMIN_KEYS['name']],
                roles=['readWriteAnyDatabase']
            )
