# -*- coding: utf-8 -*-
from .helpers import update_controller


def put(api, path, mongo_client):
    return update_controller(api, path, mongo_client, replace=True)
