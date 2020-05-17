# -*- coding: utf-8 -*-
import os
import unittest

from parameterized import parameterized

from . import mock, MONGO_PORT_AUTH
from auto_api import AutoApi
from auto_api.exceptions import AutoApiMissingAdminConfig
from auto_api.mongodb import MONGO_KEYS, ADMIN_KEYS


class AutoApiConfigAuthTest(unittest.TestCase):

    @staticmethod
    def _create_autoapi(port=None, **kwargs):
        return AutoApi(auth=True, port=port, **kwargs)

    def test_default(self):
        autoapi = self._create_autoapi()
        self.assertIsNotNone(autoapi)

    @parameterized.expand((
        ('host', {MONGO_KEYS['host']: ''}),
        ('port', {MONGO_KEYS['port']: ''}),
        ('admin', {ADMIN_KEYS['name']: ''}),
        ('password', {ADMIN_KEYS['password']: ''}),
    ))
    def test_missing_config(self, _, values):
        with mock.patch.dict(os.environ, values):
            with self.assertRaises(AutoApiMissingAdminConfig):
                self._create_autoapi()

    @mock.patch.dict(os.environ, {MONGO_KEYS['port']: ''})
    def test_missing_admin_values(self):
        autoapi = self._create_autoapi(port=MONGO_PORT_AUTH)
        self.assertIsNotNone(autoapi)


if __name__ == '__main__':
    unittest.main()
