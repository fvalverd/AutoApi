# -*- coding: utf-8 -*-
import json
import unittest

import mock

from base_test import BaseTest


class TestAuth(BaseTest):

    @mock.patch('ApiSDF._is_authorized_token', return_value=False)
    def test_unauthorized_verbs(self, _is_authorized_token_mock):
        for verb in [self.app.get, self.app.post, self.app.put, self.app.delete]:
            response = verb('/resource')
            self.assertEqual(response.status_code, 401)
            response_json = json.loads(response.data or '{}')
            self.assertDictEqual(response_json, {'message': u'You must login first'})

    @mock.patch('ApiSDF._login', return_value='Token')
    def test_token(self, _login_mock):
        data = {'email': 'admin@email.com', 'password': u'123456789'}
        response = self.app.post('/', data=data)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(response_json, {'token': u'Token'})

    def test_incomplete_login(self):
        data = {'password': u'123456789'}
        response = self.app.post('/', data=data)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(response_json, {'message': u'You must provide a proper email/password'})

    @mock.patch('ApiSDF._login', return_value=None)
    def test_bad_login_admin(self, _login_mock):
        data = {'email': 'admin@email.com', 'password': u'123456789'}
        response = self.app.post('/', data=data)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(response_json, {'message': u'You must provide a proper email/password'})

    @mock.patch('ApiSDF._create_token', return_value='Token')
    def test_login_admin(self, _create_token_mock):
        data = {'email': 'admin@email.com', 'password': u'123456789'}
        response = self.app.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(response_json, {'token': u'Token'})


if __name__ == '__main__':
    unittest.main()
