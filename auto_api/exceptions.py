# -*- coding: utf-8 -*-


class AutoApiMissingAdminConfig(Exception):
    pass


class Message(Exception):

    def __init__(self, message):
        super(Message, self).__init__()
        self.message = message
