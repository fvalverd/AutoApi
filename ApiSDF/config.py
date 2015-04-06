# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask.ext.cors import CORS


class DefaultConfig(object):
    SECRET_KEY = u'You cannot simultaneously prevent and prepare for war.'
    APISDF_DB = 'ApiSDF'
    APISDF_ADMIN = 'api_admin'
    APISDF_ADMIN_PASS = 'admin'


def config_app(app):
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(DefaultConfig)
    try:
        app.config.from_envvar('APISDF_SETTINGS')
    except:
        pass
    _create_api_admin_user(app)


def _create_api_admin_user(app):
    mongo = MongoClient(
        host=app.config['MONGO_HOST'],
        port=app.config['MONGO_PORT']
    )
    admin = app.config['MONGO_ADMIN']
    admin_password = app.config['MONGO_ADMIN_PASS']
    if mongo.admin.authenticate(admin, admin_password):
        mongo[app.config['APISDF_DB']].add_user(
            app.config['APISDF_ADMIN'],
            app.config['APISDF_ADMIN_PASS'],
            roles=[
                {'role': 'dbOwner', 'db': app.config['APISDF_DB']}
            ]
        )
        mongo[app.config['APISDF_DB']].logout()
