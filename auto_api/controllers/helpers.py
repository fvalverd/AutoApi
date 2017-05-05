# -*- coding: utf-8 -*-
from contextlib import contextmanager

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request

from ..exceptions import Message
from ..messages import invalid, not_allow, not_found, ok_no_data
from ..utils import proccess_path


@contextmanager
def autoapi_data(path, collections=False):
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = proccess_path(path=path)
    conditions = {key: {'$in': [value]} for key, value in conditions.items()}
    if resource_id is None and not collections:
        raise Message(not_allow(u'Collections do not support this operation'))
    try:
        conditions.update({'_id': ObjectId(resource_id)})
        params.update({'_id': conditions['_id']})
    except InvalidId:
        raise Message(invalid(u'Resource "%s" is invalid' % resource_id))
    yield resource_id, collection, conditions, params


def update_controller(api, path, client, replace=False):
    try:
        with autoapi_data(path) as (
            resource_id, collection, conditions, params
        ):
            # Update query
            operations = params if replace else {'$set': params}
            result = client[api][collection].update(conditions, operations)
            if result['n'] == 0:
                return not_found(u'Resource "%s" not found' % resource_id)
            return ok_no_data()
    except Message, m:
        return m.message
