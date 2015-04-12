# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask.ext.cors import CORS

from ApiSDF.auth import _admin_manager_client


class DefaultConfig(object):
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_ADMIN = 'admin'
    MONGO_ADMIN_PASS = 'pass'


def config_app(app):
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(DefaultConfig)
    app.config.from_envvar('APISDF_SETTINGS')
    with _admin_manager_client(app) as client:
        client.admin.command(
            'grantRolesToUser',
            app.config['MONGO_ADMIN'],
            roles=['readWriteAnyDatabase']
        )
