# -*- coding: utf-8 -*-
import json

from flask import request, Response

from ApiSDF.utils import proccess_path


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
