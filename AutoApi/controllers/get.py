# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Response, request

from AutoApi.utils import format_result, proccess_path


DEFAULT_PARAMS = ['_limit', '_sort']


def get(api, path, mongo_client):
    status = 200
    resource_id, collection, conditions = proccess_path(path=path)
    if resource_id is None:
        conditions.update({
            field: request.args[field]
            for field in request.args if field not in DEFAULT_PARAMS
        })
        limit = request.args.get('_limit')
        limit = cursor.limit(int(limit) if limit and limit.isdigit() else 10)
        sort_by = request.args.get('_sort', '_id')
        sort_by = cursor.sort([(sort_by, -1 if '-' in sort_by else 1)])
        cursor = mongo_client[api][collection].find(conditions).skip(0)
        cursor = cursor.skip(0).limit(limit).sort(sort_by)
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
