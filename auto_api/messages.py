# -*- coding: utf-8 -*-
import json

from flask import Response


def ok_no_data():
    return Response(status=204)


def response(data, headers=None, status=200):
    return Response(
        headers=headers,
        mimetype="application/json",
        response=json.dumps(data),
        status=status
    )


def message(text, headers=None, status=200):
    return response({'message': text}, headers=headers, status=status)


def unauthenticated():
    return message(u'Invalid email/password/api', status=400)


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
