# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from flask import Flask, jsonify, request, Response

from ApiSDF.auth import login_and_get_token, logout_and_remove_token, secure
from ApiSDF.config import config_app
from ApiSDF.utils import format_result


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
    return jsonify({'message': u'You must provide a proper email/password'}), 400


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
        collection_name = elements[-1]
        if collection_name in db.collection_names():
            results = db[collection_name].find({}).limit(10).skip(0).sort([('_id', -1)])
            total = results.count()
            results = [format_result(element) for element in results]
            return jsonify({'total': len(results), collection_name: results})
        else:
            return jsonify({'message': u'Collection id not found'}), 404
    else:
        collection_name = elements[-2]
        resource_id = elements[-1]
        result = db[collection_name].find_one({'_id': ObjectId(resource_id)})
        if result is not None:
            return jsonify(format_result(result))
        else:
            return jsonify({'message': u'Resource id not found'}), 404


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
