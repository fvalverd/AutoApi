# -*- coding: utf-8 -*-
import json

from flask import request, Response

from ApiSDF.auth import login_and_get_token, logout_and_remove_token


def login(app):
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
                response=json.dumps({
                    'email': params.get('email'),
                    'token': token
                }),
                headers={
                    'X-Email': params.get('email'),
                    'X-Token': token
                }
            )
    return Response(
        response=json.dumps({'message': u'Invalid email/password/api'}),
        status=400
    )


def logout(app, mongo_client):
    params = request.json or request.form.to_dict()
    if logout_and_remove_token(app, params.get('api')):
        return Response(status=204)
    return Response(
        response=json.dumps({'message': u'Invalid email/password/api'}),
        status=400
    )


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
