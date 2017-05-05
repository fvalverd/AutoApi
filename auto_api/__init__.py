# -*- coding: utf-8 -*-
import json

from flask import Flask

from .auth import login, logout, password, roles, secure, user
from .config import config
from .controllers import get, post, delete, put, patch


class AutoApi(object):

    def __init__(self, auth=False, cors=True, config_path=None, port=None):
        self.auth = auth
        self.app = Flask(self.__class__.__name__)
        config(self, cors=cors, path=config_path, force_port=port)
        self.load_auth()
        self.load_methods()

    def route(
        self, force_no_auth=False, method='POST',
        path='/<api>/<path:path>', role=None
    ):
        def wrapper(controller):
            return self.app.route(path, methods=[method])(
                secure(
                    self.app,
                    role=role,
                    auth=self.auth and not force_no_auth
                )(controller)
            )
        return wrapper

    def load_auth(self):
        # TODO: add invalid operation for /not_valid_op
        if self.auth:
            self.route(path='/login', force_no_auth=True)(login)
            self.route(path='/logout')(logout)
            self.route(path='/user', role='admin')(user)
            self.route(path='/password')(password)
            self.route(path='/roles', role='admin')(roles)

    def load_methods(self):
        self.route(method='GET', role='read')(get)
        self.route(method='POST', role='create')(post)
        self.route(method='DELETE', role='delete')(delete)
        self.route(method='PUT', role='update')(put)
        self.route(method='PATCH', role='update')(patch)

    def run(self, host='0.0.0.0', port=8686, reloader=True, debug=True):
        self.app.run(host=host, port=port, use_reloader=reloader, debug=debug)
