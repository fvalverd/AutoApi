# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request, Response

from ApiSDF.auth import login_and_get_token, logout_and_remove_token, secure
from ApiSDF.config import config_app
from ApiSDF.utils import format_result, proccess_path


app = Flask('ApiSDF')
config_app(app)


@app.route("/", methods=['POST'])
def login():
    params = request.json or request.form.to_dict()
    if params.get('email'):
        token = login_and_get_token(
            app,
            email=params.get('email'),
            password=params.get('password')
        )
        if token is not None:
            return Response(
                response=json.dumps({'token': token}),
                headers={
                    'X-Email': params.get('email'),
                    'X-Token': token
                }
            )
    return jsonify({'message': u'Invalid email/password'}), 400


@app.route("/", methods=['DELETE'])
@secure(app)
def logout(db):
    status = logout_and_remove_token(app, db)
    return jsonify({}), 204


@app.route('/<path:path>', methods=['GET'])
@secure(app)
def get(path, db):
    status = 200
    json_to_response = '{}'
    resource_id, collection, conditions = proccess_path(path=path)
    if resource_id is None:
        cursor = db[collection].find(conditions)
        cursor = cursor.limit(10).skip(0).sort([('_id', -1)])
        total = cursor.count()
        results = [format_result(element) for element in cursor]
        json_to_response = jsonify({
            'total': len(results),
            collection: results
        })
    else:
        try:
            conditions.update({'_id': ObjectId(resource_id)})
        except InvalidId:
            json_to_response = jsonify({
                'message': u'Resource "%s" is invalid' % resource_id
            })
            status = 404
        else:
            result = db[collection].find_one(conditions)
            if result is not None:
                json_to_response = jsonify(format_result(result))
            else:
                json_to_response = jsonify({
                    'message': u'Resource "%s" not found' % resource_id
                })
                status = 404
    return json_to_response, status


@app.route('/<path:path>', methods=['POST'])
@secure(app, 'write')
def post(path, db):
    params = request.json or request.form.to_dict()
    resource_id, collection, data = proccess_path(path=path, params=params)
    if resource_id is None:
        resource_id = db[collection].insert(data)
        if resource_id is not None:
            resource_id = str(resource_id)
            return Response(
                response=json.dumps({'id': resource_id}),
                headers={
                    'Location': '/%s/%s' % (collection, resource_id),
                },
                status=201
            )
    else:
        return jsonify({'message': u'Not supported resource creation'}), 405


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
