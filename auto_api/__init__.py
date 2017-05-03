# -*- coding: utf-8 -*-
import json

from flask import Flask

from .auth import login, logout, password, roles, secure, user
from .config import config
from .controllers import get, post, delete, put, patch


class AutoApi(object):

    def __init__(self, auth=False):
        self.auth = auth
        self.app = Flask(self.__class__.__name__)
        config(self.app)
        self.load_auth()
        self.load_verbs()

    def route(self, path, method, role=None, auth=True):
        def wrapper(controller):
            return self.app.route(path, methods=[method])(
                secure(self.app, role=role, auth=auth)(controller)
            )
        return wrapper

    def load_auth(self):
        # TODO: add invalid operation for /not_valid_op
        if self.auth:
            self.route('/login', 'POST', auth=False)(login)
            self.route('/logout', 'POST')(logout)
            self.route('/user', 'POST', role='admin')(user)
            self.route('/password', 'POST')(password)
            self.route('/roles', 'POST', role='admin')(roles)

    def load_verbs(self):
        path = '/<api>/<path:path>'
        self.route(path, 'GET', role='read')(get)
        self.route(path, 'POST', role='create')(post)
        self.route(path, 'DELETE', role='delete')(delete)
        self.route(path, 'PUT', role='update')(put)
        self.route(path, 'PATCH', role='update')(patch)

    def run(host='0.0.0.0', port=8686, use_reloader=True, debug=True):
        self.app.run(
            host=host,
            port=port,
            use_reloader=use_reloader,
            debug=debug
        )
