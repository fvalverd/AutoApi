# -*- coding: utf-8 -*-
import json
import logging

from flask import Flask

from .auth import add_app, secure, login, logout, user, password, roles
from .config import config_app
from .controllers import get, post, delete, put, patch


app = Flask('AutoApi')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARN)
app.logger.addHandler(stream_handler)
config_app(app)


app.route('/login', methods=['POST'])(
    add_app(app, controller=login)
)

app.route('/logout', methods=['POST'])(
    secure(app, controller=logout)
)

app.route('/user', methods=['POST'])(
    secure(app, controller=user, role='admin')
)

app.route('/password', methods=['POST'])(
    secure(app, controller=password)
)

app.route('/roles', methods=['POST'])(
    secure(app, controller=roles, role='admin')
)


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
