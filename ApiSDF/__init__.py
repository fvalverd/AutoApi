# -*- coding: utf-8 -*-
import json

from flask import Flask

from ApiSDF.auth import add_app, login_and_get_token, logout_and_remove_token, \
    secure
from ApiSDF.config import config_app
from ApiSDF.controllers import login, logout, create_user, get, post, \
    delete, put, patch


app = Flask('ApiSDF')
config_app(app)


app.route('/login', methods=['POST'])(
    add_app(app, controller=login)
)

app.route('/logout', methods=['POST'])(
    secure(app, logout=True, role=['*'], controller=logout)
)

app.route('/create_user', methods=['POST'])(
    secure(app, api='admin', role=['admin'], controller=create_user)
)

app.route('/<api>/<path:path>', methods=['GET'])(
    secure(app, role=['read'], controller=get)
)

app.route('/<api>/<path:path>', methods=['POST'])(
    secure(app, role=['create'], controller=post)
)

app.route('/<api>/<path:path>', methods=['DELETE'])(
    secure(app, role=['delete'], controller=delete)
)

app.route('/<api>/<path:path>', methods=['PUT'])(
    secure(app, role=['update'], controller=put)
)

app.route('/<api>/<path:path>', methods=['PATCH'])(
    secure(app, role=['update'], controller=patch)
)
