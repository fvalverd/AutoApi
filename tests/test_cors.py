# -*- coding: utf-8 -*-
import unittest

from auto_api import AutoApi
from . import MONGO_PORT, MONGO_AUTH_PORT


class AutoApiConfigTest(unittest.TestCase):

    def _test_header(self, autoapi):
        response = autoapi.app.test_client().get('/')
        (self.assertIn if autoapi.cors else self.assertNotIn)(
            ('Access-Control-Allow-Origin', '*'),
            response.headers.to_wsgi_list()
        )

    def test_access_control_allow_origin_header(self):
        self._test_header(AutoApi(port=MONGO_PORT))

    def test_access_control_allow_origin_header_no_cors(self):
        self._test_header(AutoApi(port=MONGO_PORT, cors=False))

    def test_access_control_allow_origin_header_with_auth(self):
        self._test_header(AutoApi(auth=True, port=MONGO_AUTH_PORT))

    def test_access_control_allow_origin_header_with_auth_no_cors(self):
        self._test_header(AutoApi(auth=True, port=MONGO_AUTH_PORT, cors=False))


if __name__ == '__main__':
    unittest.main()
