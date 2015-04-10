# -*- coding: utf-8 -*-
import json
import unittest

import mock

from utils import BaseTest


class TestAuth(BaseTest):

    def test_unauthorized(self):
        for verb in [self.app.get, self.app.post, self.app.put, self.app.delete]:
            response = verb('/api_tests/movies')
            self.assertEqual(response.status_code, 401)
            response_json = json.loads(response.data or '{}')
            self.assertDictEqual(
                response_json,
                {'message': u'You must be logged in "%s" api' % u'api_tests'}
            )

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

    def test_login(self):
        data = {'email': u'api_admin', 'password': u'pass', 'api': u'api_tests'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/api_tests/movies', headers=response.headers)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        data = {'email': u'api_admin', 'password': u'pass', 'api': u'api_tests'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        session_headers = {'X-Email': data['email'], 'X-Token': response.headers['X-Token']}
        response = self.app.post('/logout', headers=session_headers, data={'api': 'api_tests'})
        self.assertEqual(response.status_code, 204)

    def test_login_but_unauthorized_in_other_api(self):
        data = {'email': u'api_admin', 'password': u'pass', 'api': u'api_tests'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/bad_api/movies', headers=response.headers)
        self.assertEqual(response.status_code, 401)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(
            response_json,
            {'message': u'You must be logged in "%s" api' % u'bad_api'}
        )

    def test_logout_but_unauthorized_in_other_api(self):
        data = {'email': u'api_admin', 'password': u'pass', 'api': u'api_tests'}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        session_headers = {'X-Email': data['email'], 'X-Token': response.headers['X-Token']}
        response = self.app.post('/logout', headers=session_headers, data={'api': 'bad_api'})
        self.assertEqual(response.status_code, 401)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(
            response_json,
            {'message': u'You must be logged in "%s" api' % u'bad_api'}
        )


if __name__ == '__main__':
    unittest.main()
