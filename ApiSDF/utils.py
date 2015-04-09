# -*- coding: utf-8 -*-


def format_result(result):
    if result is not None and result.get('_id'):
        result['id'] = str(result.pop('_id'))
        return result


def proccess_path(path='', params=None):
    elements = path.split('/')
    is_odd = len(elements) % 2 == 1
    resource_id = None if is_odd else elements.pop(-1)
    collection = elements.pop(-1)
    path_conditions = dict(zip(
        elements[0::2],
        elements[1::2] if params is None else [elements[1::2]]
    ))
    conditions = params or {}
    for key in ['id', '_id']:
        if key in conditions:
            del conditions[key]
    conditions.update(path_conditions)
    return resource_id, collection, conditions
