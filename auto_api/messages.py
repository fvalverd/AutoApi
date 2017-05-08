# -*- coding: utf-8 -*-
import datetime
import json

from bson.objectid import ObjectId


from flask import Response


def _autoapi_dumps(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()


def ok():
    return Response(status=204)


def response(data, headers=None, status=200, default_dumps=_autoapi_dumps):
    return Response(
        headers=headers, mimetype="application/json",
        response=json.dumps(data, default=default_dumps), status=status
    )


def message(text, headers=None, status=200):
    return response({'message': text}, headers=headers, status=status)


def bad_request(text):
    return message(text, status=400)


def forbidden(text):
    return message(text, status=403)


def unauthenticated():
    return message(u'Invalid email/password/api', status=401)


def unauthorized(api):
    return message(u'You must be authorized in "%s" api' % api, status=403)


def unlogged(api):
    return message(u'You must be logged in "%s" api' % api, status=401)


def not_found(text):
    return message(text, status=404)


def not_allow(text):
    return message(text, status=405)


def invalid(text):
    return message(text, status=409)
