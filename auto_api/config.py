# -*- coding: utf-8 -*-
import logging
import os

from flask_cors import CORS

from .exceptions import AutoApiMissingAdminConfig
from .mongodb import ADMIN_KEYS, MONGO_KEYS


def config_autoapi(
    autoapi, cors=True, logging_level=logging.WARN, force_port=None
):
    _config_logging(autoapi, level=logging_level)
    if cors:
        CORS(autoapi, resources={r'/*': {'origins': '*'}})
    _read_config(autoapi, force_port=force_port)


def _config_logging(autoapi, level):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    autoapi.logger.addHandler(stream_handler)


def _read_config(autoapi, force_port=None):
    if os.environ.get(MONGO_KEYS['host']):
        autoapi.config[MONGO_KEYS['host']] = os.environ[MONGO_KEYS['host']]
    else:
        raise AutoApiMissingAdminConfig('Check your configuration !')
    if force_port is not None:
        autoapi.config[MONGO_KEYS['port']] = force_port
    elif os.environ.get(MONGO_KEYS['port']):
        port = int(os.environ[MONGO_KEYS['port']])
        autoapi.config[MONGO_KEYS['port']] = port
    else:
        raise AutoApiMissingAdminConfig('Check your configuration !')
    if autoapi.auth:
        # Read MongoDB admin credentials
        for key in ADMIN_KEYS.values():
            if os.environ.get(key):
                autoapi.config[key] = os.environ[key]
            else:
                raise AutoApiMissingAdminConfig('Check your configuration !')
