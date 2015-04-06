# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from flask import Flask, Response, request, jsonify

from config import config_app
from auth import secure, login_and_get_token, logout_and_remove_token


app = Flask('ApiSDF')
config_app(app)


@app.route("/", methods=['POST'])
def login():
    params = request.json or request.form.to_dict()
    if params.get('email'):
        token = login_and_get_token(app, email=params.get('email'), password=params.get('password'))
        if token is not None:
            return Response(
                response=json.dumps({'token': token}),
                headers={'X-Email': params.get('email'), 'X-Token': token}
            )
    return Response(response=json.dumps({'message': u'You must provide a proper email/password'}), status=400)


@app.route("/", methods=['DELETE'])
@secure(app)
def logout(db):
    status = logout_and_remove_token(app, db)
    return jsonify({'ok': status})


def _proccess_path(path=''):
    elements = path.split('/')
    return len(elements) % 2 == 1, elements


@app.route('/<path:path>', methods=['GET'])
@secure(app)
def get(path, db):
    is_odd, elements = _proccess_path(path=path)
    if is_odd:
        results = db[elements[-1]].find({}).limit(10).skip(0).sort([('_id', -1)])
        total = results.count()
        results = [element for element in results]
        return jsonify({'total': len(results), 'data': results})
    else:
        result = db[elements[-2]].find_one({'_id': ObjectId(elements[-1])}) or {}
        return jsonify(result)


@app.route('/<path:path>', methods=['POST'])
@secure(app, 'write')
def post(path, db):
    pass


@app.route('/<path:path>', methods=['PUT'])
@secure(app, 'write')
def put(path, db):
    pass


@app.route('/<path:path>', methods=['PATCH'])
@secure(app, 'write')
def patch(path, db):
    pass


@app.route('/<path:path>', methods=['DELETE'])
@secure(app, 'write')
def delete(path, db):
    pass
