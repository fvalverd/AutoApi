# -*- coding: utf-8 -*-
from ..messages import bad_request


def invalid_operation(api):
    return bad_request(u'This is not a valid operation')
