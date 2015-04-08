# -*- coding: utf-8 -*-
import json
import unittest

import mock

from utils import MoviesTest


class TestGet(MoviesTest):

    @classmethod
    def setUpClass(cls):
        super(TestGet, cls).setUpClass()
        response = cls.app.post('/', data={'email': u'api_admin', 'password': u'pass'})
        cls.headers = {'X-Email': response.headers['X-Email'], 'X-Token': response.headers['X-Token']}

    @classmethod
    def tearDownClass(cls):
        cls.app.delete('/', headers=cls.headers)
        super(TestGet, cls).tearDownClass()

    def test_get_not_created_collection(self):
        response = self.app.get('/countries', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Collection id not found'}, response_json)

    def test_get_not_created_resource(self):
        response = self.app.get('/countries/%s' % self.movies[0]['id'], headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Resource id not found'}, response_json)

    def test_get_collection(self):
        response = self.app.get('/movies', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'total': len(self.movies)}, response_json)
        self.assertIn('movies', response_json)
        self.assertItemsEqual(self.movies, response_json['movies'])

    def test_get_resource_id(self):
        response = self.app.get('/movies/%s' % self.movies[0]['id'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    # TODO: nested requests


if __name__ == '__main__':
    unittest.main()
