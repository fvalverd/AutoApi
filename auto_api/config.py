# -*- coding: utf-8 -*-
import logging

from flask_cors import CORS

from .exceptions import AutoApiMissingAdminConfig
from .mongodb import ADMIN_KEYS, MONGO_KEYS


AUTOAPI_SETTINGS_VAR = 'AUTOAPI_SETTINGS'


def config_autoapi(
    autoapi, cors=True, logging_level=logging.WARN,
    path=None, force_port=None
):
    _config_logging(autoapi, level=logging_level)
    if cors:
        CORS(autoapi.app, resources={r'/*': {'origins': '*'}})
    _read_config(autoapi, path, force_port=force_port)


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

    missing_values = any(
        key not in autoapi.app.config for key in ADMIN_KEYS.values()
    )
    if autoapi.auth and missing_values:
        raise AutoApiMissingAdminConfig('Check your configuration !')
