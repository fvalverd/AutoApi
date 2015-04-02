# -*- coding: utf-8 -*-
import json
import unittest

import mock

from ApiSDF import app


app = app.test_client()


class TestAuth(unittest.TestCase):

    @mock.patch('ApiSDF._create_token', return_value='Token')
    def test_login(self, _get_token_mock):
        data = {'email': 'admin@email.com', 'password': '123456789'}
        response = app.post('/', data=data)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(response_json, {'token': 'Token'})

    @mock.patch('ApiSDF._is_authorized_token', return_value=False)
    def test_unauthorized_verbs(self, _get_token_mock):
        for verb in [app.get, app.post, app.put, app.delete]:
            response = verb('/resource')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data, 'You must login first')


if __name__ == '__main__':
    unittest.main()
