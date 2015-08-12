# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Response, request

from AutoApi.utils import format_result, proccess_path


DEFAULTS = {
    '_sort': '_id',
    '_limit': 10,
    '_skip': 0,
    '_regex': False
}


def get(api, path, mongo_client):
    status = 200
    resource_id, collection, conditions = proccess_path(path=path)
    if resource_id is None:
        conditions.update({
            field: request.args[field]
            for field in request.args if field not in DEFAULTS
        })
        sort_by = request.args.get('_sort') or DEFAULTS['_sort']
        sort_by = [(
            sort_by[1:] if '-' == sort_by[0] else sort_by,
            -1 if '-' == sort_by[0] else 1
        )]
        limit = request.args.get('_limit')
        limit = int(limit) if limit and limit.isdigit() else DEFAULTS['_limit']
        skip = request.args.get('_skip')
        skip = int(skip) if skip and skip.isdigit() else DEFAULTS['_skip']
        if request.args.get('_regex') in conditions:
            conditions[request.args.get('_regex')] = {
                '$regex': conditions[request.args.get('_regex')],
                '$options': 'i'
            }
        cursor = mongo_client[api][collection].find(conditions)
        cursor = cursor.sort(sort_by).limit(limit).skip(skip)
        response = json.dumps([format_result(element) for element in cursor])
    else:
        try:
            conditions.update({'_id': ObjectId(resource_id)})
        except InvalidId:
            response = json.dumps({
                'message': u'Resource "%s" is invalid' % resource_id
            })
            status = 404
        else:
            result = mongo_client[api][collection].find_one(conditions)
            if result is not None:
                response = json.dumps(format_result(result))
            else:
                response = json.dumps({
                    'message': u'Resource "%s" not found' % resource_id
                })
                status = 404
    return Response(
        response=response,
        headers={'Content-Type': 'application/%s+json' % (
            'collection' if resource_id is None else 'resource'
        )},
        status=status
    )
