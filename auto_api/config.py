# -*- coding: utf-8 -*-
import logging

from pymongo import MongoClient
from flask_cors import CORS

from .auth import _admin_manager_client


def autoapi_config(app):
    # loggin
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARN)
    app.logger.addHandler(stream_handler)

    # cross domain
    CORS(app, resources={r"/*": {"origins": "*"}})

    # autoapi config file
    app.config.from_envvar('AUTOAPI_SETTINGS')

    # autoapi admin config
    with _admin_manager_client(app) as client:
        try:
            client.admin.add_user(
                app.config['MONGO_ADMIN'],
                app.config['MONGO_ADMIN_PASS'],
                roles=[
                    {'role': 'userAdminAnyDatabase', 'db': 'admin'}
                ],
                customData={
                    'roles': ['admin']
                }
            )
        except:
            pass
        with _admin_manager_client(app, client=client) as client:
            client.admin.command(
                'grantRolesToUser',
                app.config['MONGO_ADMIN'],
                roles=['readWriteAnyDatabase']
            )
