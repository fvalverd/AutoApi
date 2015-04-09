# -*- coding: utf-8 -*-
import json
import unittest

import mock

from utils import BaseTest


class TestLogin(BaseTest):

    def test_incomplete_login(self):
        data = {'password': u'pass'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Invalid email/password/api'}, response_json)

    def test_login_bad_pass(self):
        data = {'email': u'api_admin', 'password': u'bad_pass', 'api': 'api_tests'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Invalid email/password/api'}, response_json)

    @mock.patch('ApiSDF.auth._create_token', return_value='MockedToken')
    def test_login_admin(self, _create_and_save_token_mock):
        data = {'email': u'api_admin', 'password': u'pass', 'api': 'api_tests'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'token': u'MockedToken'}, response_json)
        self.assertDictContainsSubset(
            {'X-Email': data['email'], 'X-Token': u'MockedToken'},
            dict(response.headers)
        )


if __name__ == '__main__':
    unittest.main()
