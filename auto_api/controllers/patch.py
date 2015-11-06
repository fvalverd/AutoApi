# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request, Response

from ..utils import proccess_path


def patch(api, path, mongo_client):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = proccess_path(path=path)
    json_dumped = None
    status = 204
    if resource_id is None:
        json_dumped = json.dumps({
            'message': u'Not supported collection update'
        })
        status = 404
    else:
        try:
            conditions = {
                key: {'$in': [value]}
                for key, value in conditions.items()
            }
            conditions.update({'_id': ObjectId(resource_id)})
        except InvalidId:
            json_dumped = json.dumps({
                'message': u'Resource "%s" is invalid' % resource_id
            })
            status = 404
        else:
            params['_id'] = conditions['_id']
            result = mongo_client[api][collection].update(
                conditions,
                {'$set': params}
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
