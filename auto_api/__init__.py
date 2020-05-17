# -*- coding: utf-8 -*-
from flask import Flask
from flask.views import http_method_funcs

from .auth import secure
from .config import config_autoapi
from .messages import message
from .operations import invalid_operation, login, logout, password, roles, user
from .views import get, post, delete, put, patch


class AutoApi(Flask):

    def __init__(self, auth=False, cors=True, port=None):
        super(AutoApi, self).__init__(self.__class__.__name__)
        self.auth = auth
        self.cors = cors
        config_autoapi(self, cors=cors, force_port=port)

        # AutoApi operation routes
        self.prefix = 'AutoApi'
        self.load_operations()

        # Customize routes
        self.prefix = self.__class__.__name__
        self.load_more_routes()

        # AutoApi rest routes
        self.prefix = 'AutoApi'
        self.load_api_rest()

    def welcome(self):
        return message('Welcome to AutoApi.')

    def _name(self, view):
        return '{prefix}.{name}'.format(prefix=self.prefix, name=view.__name__)

    def add(
        self, path, view, api=None, skip_auth=False,
        method='POST', role=None, all_methods=False, no_api=False
    ):
        """" Bind path with view on AutoApi """

        auth = self.auth and not skip_auth
        params = dict(view=view, role=role, api=api, auth=auth, no_api=no_api)
        self.add_url_rule(
            path, endpoint=self._name(view), view_func=secure(self, **params),
            methods=all_methods and list(http_method_funcs) or [method]
        )

    def route(self, path, **kwargs):
        """ Decorator to bind path with view on AutoApi """

        def wrapper(view):
            self.add(path, view, **kwargs)
        return wrapper

    def load_operations(self):
        """ Bind operations related with Authentication & Authorization """
        skip_all_params = dict(skip_auth=True, all_methods=True, no_api=True)

        # AutoApi welcome message
        self.add('/', lambda: self.welcome(), **skip_all_params)

        # Invalid operation message
        self.add('/<api>', invalid_operation, **skip_all_params)

        # AutoApi auth operations
        if self.auth:
            self.add('/login', login, skip_auth=True)
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
