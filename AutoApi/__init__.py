# -*- coding: utf-8 -*-
import json

from flask import Flask

from AutoApi.auth import add_app, secure, login, logout, create_user
from AutoApi.config import config_app
from AutoApi.controllers import get, post, delete, put, patch


app = Flask('AutoApi')
config_app(app)


# Users

app.route('/login', methods=['POST'])(
    add_app(app, controller=login)
)

app.route('/logout', methods=['POST'])(
    secure(app, controller=logout)
)

app.route('/create_user', methods=['POST'])(
    secure(app, controller=create_user, role='admin')
)


# Resurces

app.route('/<api>/<path:path>', methods=['GET'])(
    secure(app, controller=get, role='read')
)

app.route('/<api>/<path:path>', methods=['POST'])(
    secure(app, controller=post, role='create')
)

app.route('/<api>/<path:path>', methods=['DELETE'])(
    secure(app, controller=delete, role='delete')
)

app.route('/<api>/<path:path>', methods=['PUT'])(
    secure(app, controller=put, role='update')
)

app.route('/<api>/<path:path>', methods=['PATCH'])(
    secure(app, controller=patch, role='update')
)
