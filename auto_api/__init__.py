# -*- coding: utf-8 -*-
from flask import Flask
from flask.views import http_method_funcs

from .auth import secure
from .config import config_autoapi
from .messages import message
from .operations import invalid_operation, login, logout, password, roles, user
from .views import get, post, delete, put, patch


class AutoApi(object):

    def __init__(self, auth=False, cors=True, config_path=None, port=None):
        self.auth = auth
        self.app = Flask(self.__class__.__name__)
        config_autoapi(self, cors=cors, path=config_path, force_port=port)

        # AutoApi routes
        self.prefix = 'AutoApi'
        self.load_operations()
        self.load_api_rest()

        # Customize routes
        self.prefix = self.__class__.__name__
        self.load_more_routes()

    def welcome(self):
        return message(u"Welcome to AutoApi.")

    def add(
        self, path, view, api=None, no_auth=False,
        method='POST', role=None, all_methods=False, without_api=False
    ):
        """" Bind path with view on AutoApi """

        self.app.add_url_rule(
            rule=path,
            endpoint=u"{}.{}".format(self.prefix, view.__name__),
            view_func=secure(
                self.app, view, role=role, api=api,
                auth=self.auth and not no_auth, without_api=without_api
            ),
            methods=all_methods and list(http_method_funcs) or [method],
        )

    def route(self, path, **kwargs):
        """ Decorator to bind path with view on AutoApi """

        def wrapper(view):
            self.add(path, view, **kwargs)
        return wrapper

    def load_operations(self):
        """ Bind operations related with Authentication & Authorization """

        # AutoApi welcome message
        self.add(
            '/', lambda: self.welcome(), no_auth=True,
            all_methods=True, without_api=True
        )

        # Invalid operation message
        self.add(
            '/<api>', invalid_operation, no_auth=True,
            all_methods=True, without_api=True
        )

        # AutoApi auth operations
        if self.auth:
            self.add('/login', login, no_auth=True)
            self.add('/logout', logout)
            self.add('/user', user, role='admin')
            self.add('/password', password)
            self.add('/roles', roles, role='admin')

    def load_api_rest(self):
        """ Bind automatic API REST for AutoApi """

        path = '/<api>/<path:path>'
        self.add(path, get, method='GET', role='read')
        self.add(path, post, method='POST', role='create')
        self.add(path, delete, method='DELETE', role='delete')
        self.add(path, put, method='PUT', role='update')
        self.add(path, patch, method='PATCH', role='update')

    def load_more_routes(self):
        """ Implement this method to add more routes """

        pass
