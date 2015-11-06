# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask.ext.cors import CORS

from .auth import _admin_manager_client


def config_app(app):
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_envvar('AUTOAPI_SETTINGS')
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
