# -*- coding: utf-8 -*-
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request, Response

from ..messages import invalid, not_allow, not_found, ok_no_data
from ..utils import proccess_path


def put(api, path, mongo_client):
    # Conditions and params
    params = request.json or request.form.to_dict()
    resource_id, collection, conditions = proccess_path(path=path)
    if resource_id is None:
        return not_allow(u'Collections do not support replace operation')
    conditions = {key: {'$in': [value]} for key, value in conditions.items()}
    try:
        conditions.update({'_id': ObjectId(resource_id)})
        params['_id'] = conditions['_id']
    except InvalidId:
        return invalid(u'Resource "%s" is invalid' % resource_id)

    # Update query
    result = mongo_client[api][collection].update(conditions, params)
    if result['n'] == 0:
        return not_found(u'Resource "%s" not found' % resource_id)
    return ok_no_data()
