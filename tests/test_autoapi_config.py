# -*- coding: utf-8 -*-
import os
import unittest

from auto_api import AutoApi
from auto_api.config import AUTOAPI_SETTINGS_VAR
from auto_api.exceptions import AutoApiMissingAdminConfig
from auto_api.mongodb import ADMIN_KEYS
from . import mock, MONGO_PORT, MONGO_AUTH_PORT


UNEXISTING_PATH = "/unexisting_path"
ONLY_USER = {ADMIN_KEYS['name']: 'user'}
ONLY_PASS = {ADMIN_KEYS['password']: 'pass'}


def _raise(_class):
    def wrapper(*args, **kargs):
        raise _class()
    return wrapper


class AutoApiConfigTest(unittest.TestCase):

    @staticmethod
    def _create_autoapi(**kwargs):
        return AutoApi(port=MONGO_PORT, **kwargs)

    def test_default(self):
        autoapi = self._create_autoapi()
        self.assertIsNotNone(autoapi.app)

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_without_var_environment(self):
        autoapi = self._create_autoapi()
        self.assertIsNotNone(autoapi.app)

    @mock.patch.dict(os.environ, {AUTOAPI_SETTINGS_VAR: UNEXISTING_PATH})
    def test_with_var_environment_but_unexisting_path(self):
        with self.assertRaises(IOError):
            self._create_autoapi()

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_config_as_parameter(self):
        self._create_autoapi(config_path=os.environ[AUTOAPI_SETTINGS_VAR])

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_config_as_parameter_but_unexisting_path(self):
        with self.assertRaises(IOError):
            self._create_autoapi(config_path=UNEXISTING_PATH)


class AutoApiConfigAuthTest(unittest.TestCase):

    @staticmethod
    def _create_autoapi(port=True, **kwargs):
        return AutoApi(auth=True, port=port and MONGO_AUTH_PORT, **kwargs)

    def test_default(self):
        autoapi = self._create_autoapi()
        self.assertIsNotNone(autoapi.app)

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    def test_default_missing_config(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            self._create_autoapi()

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    @mock.patch.dict(os.environ, ONLY_USER)
    def test_default_only_user(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            self._create_autoapi()

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    @mock.patch.dict(os.environ, ONLY_PASS)
    def test_default_only_pass(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            self._create_autoapi()

    @mock.patch('flask.Config.from_envvar', _raise(RuntimeError))
    @mock.patch.dict(os.environ, {})
    def test_missing_admin_values(self):
        with self.assertRaises(AutoApiMissingAdminConfig):
            self._create_autoapi(port=None)


if __name__ == '__main__':
    unittest.main()
