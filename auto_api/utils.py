# -*- coding: utf-8 -*-
from contextlib import contextmanager

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request

from .exceptions import Message
from .messages import bad_request, invalid, not_allow, not_found, ok


FILTERS = {'_limit': 10, '_regex': None, '_skip': 0, '_sort': '_id'}


def _ignore_id(params, conditions):
    for key in ['id', '_id']:
        if key in params:
            del params[key]
    params.update(conditions)


def fix_id(result):
    if result is not None and result.get('_id'):
        result['id'] = str(result.pop('_id'))
        return result


def split_path(path='', params=None):
    elements = path.split('/')
    is_odd = len(elements) % 2 == 1
    resource_id = None if is_odd else elements.pop(-1)
    collection = elements.pop(-1)
    params = {} if params is None else params
    _ignore_id(params, dict(zip(elements[0::2], elements[1::2])))
    return resource_id, collection, params


def get_api(without_api=False):
    params = request.json or request.form.to_dict()
    api = params.get('api')
    if api is not None or without_api:
        return api
    raise Message(bad_request(u'Missing "api" parameter'))


@contextmanager
def autoapi_data(path, collections=False):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = split_path(path=path)
    conditions = {key: {'$in': [value]} for key, value in conditions.items()}
    if resource_id is None and not collections:
        raise Message(not_allow(u'Collections do not support this operation'))
    try:
        conditions.update({'_id': ObjectId(resource_id)})
        params.update({'_id': conditions['_id']})
    except InvalidId:
        raise Message(invalid(u'Resource "%s" is invalid' % resource_id))
    yield (resource_id, collection, conditions, params)


def update_view(api, path, client, replace=False):
    with autoapi_data(path) as (resource_id, collection, conditions, params):
        operations = params if replace else {'$set': params}
        result = client[api][collection].update(conditions, operations)
        if result['n'] == 0:
            return not_found(u'Resource "%s" not found' % resource_id)
        return ok()


def processes_filters(conditions):
    args = request.args.to_dict()
    conditions.update({key: args[key] for key in args if key not in FILTERS})
    args.update({key: FILTERS[key] for key in FILTERS if not args.get(key)})
    sort_by, regex = args['_sort'], args['_regex']
    sort_by = [(sort_by[1:], -1) if sort_by.startswith('-') else (sort_by, 1)]
    if regex is not None and regex in conditions:
        conditions[regex] = {'$regex': conditions[regex], '$options': 'i'}
    return (int(args['_limit']), int(args['_skip']), sort_by)
