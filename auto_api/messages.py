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


def message(message, headers=None, status=200):
    return response({'message': message}, headers=headers, status=status)


def invalid():
    return message(u'Invalid email/password/api', status=400)


def unauthorized(api):
    return message(u'You must be authorized in "%s" api' % api, status=403)


def unlogged(api):
    return message(u'You must be logged in "%s" api' % api, status=401)
