# -*- coding: utf-8 -*-
import os
import unittest

import mock

from auto_api import AutoApi
from auto_api.config import AUTOAPI_SETTINGS_VAR
from auto_api.exceptions import AutoApiMissingAdminConfig
from auto_api.mongodb import ADMIN_KEYS


UNEXISTING_PATH = "/unexisting_path"
ONLY_USER = {ADMIN_KEYS['user']: 'user'}
ONLY_PASS = {ADMIN_KEYS['pass']: 'pass'}


def _raise(_class):
    def wrapper(*args, **kargs):
        raise _class()
    return wrapper


class AutoApiConfigTest(unittest.TestCase):

    def test_default(self):
        autoapi = AutoApi()
        self.assertIsNotNone(autoapi.app)

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_without_var_environment(self):
        autoapi = AutoApi()
        self.assertIsNotNone(autoapi.app)

    @mock.patch.dict(os.environ, {AUTOAPI_SETTINGS_VAR: UNEXISTING_PATH})
    def test_with_var_environment_but_unexisting_path(self):
        with self.assertRaises(IOError):
            AutoApi()

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_config_as_parameter(self):
        AutoApi(config_path=os.environ[AUTOAPI_SETTINGS_VAR])

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_config_as_parameter_but_unexisting_path(self):
        with self.assertRaises(IOError):
            AutoApi(config_path=UNEXISTING_PATH)


class AutoApiConfigAuthTest(unittest.TestCase):

    def test_default(self):
        autoapi = AutoApi(auth=True)
        self.assertIsNotNone(autoapi.app)

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_default_missing_config(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            AutoApi(auth=True)

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    @mock.patch.dict(os.environ, ONLY_USER)
    def test_default_only_user(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            AutoApi(auth=True)

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    @mock.patch.dict(os.environ, ONLY_PASS)
    def test_default_only_pass(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            AutoApi(auth=True)


if __name__ == '__main__':
    unittest.main()
