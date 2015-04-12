# -*- coding: utf-8 -*-
import json
import unittest

from utils import MoviesTest


class TestGetResource(MoviesTest):

    def test_get_not_created(self):
        response = self.app.get('/api_tests/actors/%s' % self.movies[0]['id'], headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[0]['id']},
            response_json
        )

    def test_get_invalid_id(self):
        response = self.app.get('/%s/movies/a1' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, response_json)

    def test_get(self):
        response = self.app.get(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    def test_get_nested(self):
        response = self.app.get(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[0]['id'], self.movies[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    def test_get_nested_not_found(self):
        response = self.app.get(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[0]['id'], self.movies[2]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[2]['id']},
            response_json
        )


class TestGetCollection(MoviesTest):

    def test_get_not_created(self):
        response = self.app.get('/%s/countries' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('[]', response.data)

    def test_get(self):
        response = self.app.get('/%s/movies' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.movies, response_json)

    def test_get_nested(self):
        response = self.app.get(
            '/%s/actors/%s/movies' % (self.api, self.actors[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual([self.movies[0]], response_json)


if __name__ == '__main__':
    unittest.main()
