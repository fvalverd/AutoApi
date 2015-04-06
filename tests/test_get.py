# -*- coding: utf-8 -*-
import json
import unittest

import mock

from base_test import BaseTest


class TestGet(BaseTest):

    @classmethod
    def setUpClass(cls):
        super(TestGet, cls).setUpClass()
        data = {'email': u'api_admin', 'password': u'pass'}
        response = cls.app.post('/', data=data)
        cls.headers = {'X-Email': data['email'], 'X-Token': response.headers['X-Token']}

    @classmethod
    def tearDownClass(cls):
        cls.app.delete('/', headers=cls.headers)
        super(TestGet, cls).tearDownClass()

    def test_get_not_created_resource(self):
        response = self.app.get('/resource', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'total': 0, 'data': []}, response_json)

    def test_get_not_created_resource_id(self):
        response = self.app.get('/resource/52dc4e24d5d70f22c2ee9387', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual({}, response_json)

    # TODO: nested requests


if __name__ == '__main__':
    unittest.main()
