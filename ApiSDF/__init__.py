# -*- coding: utf-8 -*-
from functools import wraps
import json

from flask import Flask, Response, request, jsonify
from flask.ext.cors import CORS


app = Flask('ApiSDF')
CORS(app, resources={r"/*": {"origins": "*"}})


def _is_authorized_token():
    pass


def _create_token(email, password):
    pass


def _unauthorized():
    return Response(response='You must login first', status=401)


def auth(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs) if _is_authorized_token() else _unauthorized()
    return inner


@app.route("/", methods=['POST'])
def login():
    params = request.json or request.form.to_dict()
    result = {}
    if params.get('email'):
        token = _create_token(email=params.get('email'), password=params.get('password'))
        if token is not None:
            result['token'] = token
    return jsonify(result)


@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
@auth
def _get(path):
    pass


@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
@auth
def _post(path):
    pass


@app.route('/', defaults={'path': ''}, methods=['PUT'])
@app.route('/<path:path>', methods=['PUT'])
@auth
def _put(path):
    pass


@app.route('/', defaults={'path': ''}, methods=['DELETE'])
@app.route('/<path:path>', methods=['DELETE'])
@auth
def _delete(path):
    pass
