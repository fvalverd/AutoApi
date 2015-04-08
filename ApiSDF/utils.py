# -*- coding: utf-8 -*-


def format_result(result):
    if result is not None and result.get('_id'):
        result['id'] = str(result['_id'])
        del result['_id']
        return result
