# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request

from .exceptions import Message
from .messages import invalid, ok, message, not_allow, not_found, response
from .utils import fix_id, processes_filters, split_path, update_view


def _get_collection(api, client, collection, conditions):
    limit, skip, sort_by = processes_filters(conditions)
    cursor = client[api][collection].find(conditions)
    cursor = cursor.sort(sort_by).limit(limit).skip(skip)
    total = cursor.count()
    return {'total': total, 'items': [fix_id(item) for item in cursor]}


def _get_resource(api, client, collection, resource_id, conditions):
    try:
        conditions.update({'_id': ObjectId(resource_id)})
    except InvalidId:
        raise Message(invalid(u'Resource "%s" is invalid' % resource_id))
    item = client[api][collection].find_one(conditions)
    if item is None:
        raise Message(not_found(u'Resource "%s" not found' % resource_id))
    return fix_id(item)


def get(api, path, client):
    resource_id, collection, conditions = split_path(path=path)
    if resource_id is None:
        data = _get_collection(api, client, collection, conditions)
    else:
        data = _get_resource(api, client, collection, resource_id, conditions)
    return response(data)


def delete(api, path, client):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = split_path(path=path, params=params)
    if resource_id is not None:
        try:
            conditions.update({'_id': ObjectId(resource_id)})
        except InvalidId:
            return invalid(u'Resource "%s" is invalid' % resource_id)
    result = client[api][collection].remove(conditions)
    if result['n'] == 0 and resource_id is not None:
        return not_found(u'Resource "%s" not found' % resource_id)
    return ok()


def post(api, path, client):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = split_path(path=path, params=params)
    if resource_id is None:
        if client[api][collection].insert_one(conditions).acknowledged:
            conditions['id'] = str(conditions.pop('_id'))
            return response(conditions, status=201, headers={
                'Location': '/%s/%s/%s' % (api, collection, conditions['id']),
            })
        return message(u'The resource can not be created', status=500)
    return not_allow(u'Not supported resource creation')


def patch(api, path, client):
    return update_view(api, path, client, replace=False)


def put(api, path, client):
    return update_view(api, path, client, replace=True)
