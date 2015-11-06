# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request, Response

from ..utils import proccess_path


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
