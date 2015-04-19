# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask.ext.cors import CORS

from ApiSDF.auth import _admin_manager_client


def config_app(app):
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_envvar('APISDF_SETTINGS')
    with _admin_manager_client(app) as client:
        client.admin.command(
            'grantRolesToUser',
            app.config['MONGO_ADMIN'],
            roles=['readWriteAnyDatabase']
        )
