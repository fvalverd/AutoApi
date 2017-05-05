# -*- coding: utf-8 -*-


def _update(params, conditions):
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
    _update(params, dict(zip(elements[0::2], elements[1::2])))
    return resource_id, collection, params


def get_api_from_params(request):
    params = request.json or request.form.to_dict()
    return params.get('api')
