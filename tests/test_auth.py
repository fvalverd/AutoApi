# -*- coding: utf-8 -*-
import json
import unittest

import mock

from base_test import BaseTest


class TestAuth(BaseTest):

    def test_unauthorized(self):
        for verb in [self.app.get, self.app.post, self.app.put, self.app.patch, self.app.delete]:
            response = verb('/resource')
            self.assertEqual(response.status_code, 401)
            response_json = json.loads(response.data or '{}')
            self.assertDictEqual(response_json, {'message': u'You must login first'})

    def test_get_after_login(self):
        data = {'email': 'api_admin', 'password': u'pass'}
        response = self.app.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/resource', headers={
            'X-Email': response.headers['X-Email'],
            'X-Token': response.headers['X-Token']
        })
        self.assertEqual(response.status_code, 200)

    def test_get_after_logout(self):
        data = {'email': u'api_admin', 'password': u'pass'}
        response = self.app.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        session_headers = {'X-Email': data['email'], 'X-Token': response.headers['X-Token']}
        response = self.app.delete('/', headers=session_headers)
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/resource', headers=session_headers)
        self.assertEqual(response.status_code, 401)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(response_json, {'message': u'You must login first'})


if __name__ == '__main__':
    unittest.main()
