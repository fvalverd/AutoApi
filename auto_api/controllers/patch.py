# -*- coding: utf-8 -*-
from .helpers import update_controller


def patch(api, path, mongo_client):
    return update_controller(api, path, mongo_client, replace=False)
