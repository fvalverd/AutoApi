# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Response

from ApiSDF.utils import format_result, proccess_path


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
