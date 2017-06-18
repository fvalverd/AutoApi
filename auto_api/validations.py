# -*- coding: utf-8 -*-
import re

from .exceptions import Message
from .messages import bad_request


MSG_TEMPLATE = "{} (more info in {}{})"
URL = "https://docs.mongodb.com/manual/reference/limits"
HASH = "#Restrictions-on-Database-Names-for-Unix-and-Linux-Systems"


def validate_api(api):
    if api is not None:
        if re.search('[/\. "$]', api):  # for Unix and Linux Systems
            message = 'Api can not contain the following chracters: /\. "$'
            raise Message(bad_request(MSG_TEMPLATE.format(message, URL, HASH)))
        return api.lower()  # MongoDB databases are case insensitive
