# -*- coding: utf-8 -*-


def add_conditions_into_params(params, conditions):
    for key in ['id', '_id']:
        if key in params:
            del params[key]
    params.update(conditions)


def format_result(result):
    if result is not None and result.get('_id'):
        result['id'] = str(result.pop('_id'))
        return result


def proccess_path(path='', params=None):
    elements = path.split('/')
    is_odd = len(elements) % 2 == 1
    resource_id = None if is_odd else elements.pop(-1)
    collection = elements.pop(-1)
    params = params or {}
    add_conditions_into_params(params, dict(zip(elements[0::2], elements[1::2])))
    return resource_id, collection, params
