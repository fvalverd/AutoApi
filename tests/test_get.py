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
        response = self.app.get('/api_tests/movies/a1', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, response_json)

    def test_get(self):
        response = self.app.get('/api_tests/movies/%s' % self.movies[0]['id'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    def test_get_nested(self):
        response = self.app.get(
            '/api_tests/actors/%s/movies/%s' % (self.actors[0]['id'], self.movies[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    def test_get_nested_not_found(self):
        response = self.app.get(
            '/api_tests/actors/%s/movies/%s' % (self.actors[0]['id'], self.movies[2]['id']),
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
        response = self.app.get('/api_tests/countries', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'total': 0, 'countries': []}, response_json)

    def test_get(self):
        response = self.app.get('/api_tests/movies', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'total': len(self.movies)}, response_json)
        self.assertIn('movies', response_json)
        self.assertItemsEqual(self.movies, response_json['movies'])

    def test_get_nested(self):
        response = self.app.get('/api_tests/actors/%s/movies' % self.actors[0]['id'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'total': 1}, response_json)
        self.assertIn('movies', response_json)
        self.assertItemsEqual([self.movies[0]], response_json['movies'])

if __name__ == '__main__':
    unittest.main()
