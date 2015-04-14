# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Flask, request, Response

from ApiSDF.auth import login_and_get_token, logout_and_remove_token, secure
from ApiSDF.config import config_app
from ApiSDF.utils import add_conditions_into_params, format_result, proccess_path


app = Flask('ApiSDF')
config_app(app)


@app.route("/login", methods=['POST'])
def login():
    params = request.json or request.form.to_dict()
    if params.get('email') and params.get('api'):
        token = login_and_get_token(
            app,
            params.get('api'),
            email=params.get('email'),
            password=params.get('password')
        )
        if token is not None:
            return Response(
                response=json.dumps({'email': params.get('email'), 'token': token}),
                headers={
                    'X-Email': params.get('email'),
                    'X-Token': token
                }
            )
    return Response(
        response=json.dumps({'message': u'Invalid email/password/api'}),
        status=400
    )


@app.route("/logout", methods=['POST'])
@secure(app, logout=True)
def logout(mongo_client):
    params = request.json or request.form.to_dict()
    if logout_and_remove_token(app, params.get('api')):
        return Response(status=204)
    return Response(
        response=json.dumps({'message': u'Invalid email/password/api'}),
        status=400
    )


@app.route("/create_user", methods=['POST'])
@secure(app, api='admin')
def create_user(mongo_client):
    params = request.json or request.form.to_dict()
    if params.get('email') and params.get('password') and params.get('api'):
        mongo_client[params.get('api')].add_user(
            params.get('email'),
            params.get('password'),
            roles=[
                {'role': 'dbOwner', 'db': params.get('api')}
            ]
        )
        return Response(status=201)


@app.route('/<api>/<path:path>', methods=['GET'])
@secure(app, role=['read'])
def get(api, path, mongo_client):
    status = 200
    resource_id, collection, conditions = proccess_path(path=path)
    if resource_id is None:
        cursor = mongo_client[api][collection].find(conditions)
        cursor = cursor.limit(10).skip(0).sort([('_id', -1)])
        total = cursor.count()
        json_dumped = json.dumps([format_result(element) for element in cursor])
    else:
        try:
            conditions.update({'_id': ObjectId(resource_id)})
        except InvalidId:
            json_dumped = json.dumps({
                'message': u'Resource "%s" is invalid' % resource_id
            })
            status = 404
        else:
            result = mongo_client[api][collection].find_one(conditions)
            if result is not None:
                json_dumped = json.dumps(format_result(result))
            else:
                json_dumped = json.dumps({
                    'message': u'Resource "%s" not found' % resource_id
                })
                status = 404
    return Response(
        response=json_dumped,
        headers={'Content-Type': 'application/%s+json' % (
            'collection' if resource_id is None else 'resource'
        )},
        status=status
    )


@app.route('/<api>/<path:path>', methods=['POST'])
@secure(app, role=['create'])
def post(api, path, mongo_client):
    params = request.json or request.form.to_dict()
    resource_id, collection, data = proccess_path(path=path, params=params)
    if resource_id is None:
        resource_id = mongo_client[api][collection].insert(data)
        if resource_id is not None:
            resource_id = str(resource_id)
            return Response(
                response=json.dumps({'id': resource_id}),
                headers={
                    'Location': '/%s/%s/%s' % (api, collection, resource_id),
                },
                status=201
            )
    else:
        return Response(
            response=json.dumps({
                'message': u'Not supported resource creation'
            }),
            status=405
        )


@app.route('/<api>/<path:path>', methods=['DELETE'])
@secure(app, role=['delete'])
def delete(api, path, mongo_client):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = proccess_path(
        path=path,
        params=params
    )
    try:
        if resource_id is not None:
            conditions.update({'_id': ObjectId(resource_id)})
    except InvalidId:
        return Response(
            response=json.dumps({
                'message': u'Resource "%s" is invalid' % resource_id
            }),
            status=404
        )
    else:
        result = mongo_client[api][collection].remove(conditions)
        if result['n'] == 0 and resource_id is not None:
            return Response(
                response=json.dumps({
                    'message': u'Resource "%s" not found' % resource_id
                }),
                status=404
            )
        return Response(status=204)


@app.route('/<api>/<path:path>', methods=['PUT'])
@secure(app, role=['create', 'update'])
def put(api, path, mongo_client):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = proccess_path(path=path)
    json_dumped = None
    status = 204
    if resource_id is None:
        json_dumped = json.dumps({
            'message': u'Not supported collection update/replace'
        })
        status = 404
    else:
        try:
            conditions = {key: {'$in': [value]} for key, value in conditions.items()}
            conditions.update({'_id': ObjectId(resource_id)})
        except InvalidId:
            json_dumped = json.dumps({
                'message': u'Resource "%s" is invalid' % resource_id
            })
            status = 404
        else:
            result = mongo_client[api][collection].update(
                conditions,
                params
            )
            if result['n'] == 0:
                json_dumped = json.dumps({
                    'message': u'Resource "%s" not found' % resource_id
                })
                status = 404
    return Response(
        response=json_dumped,
        status=status
    )


@app.route('/<api>/<path:path>', methods=['PATCH'])
@secure(app, role=['update'])
def patch(api, path, mongo_client):
    pass
