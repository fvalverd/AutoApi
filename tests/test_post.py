# -*- coding: utf-8 -*-
import json
import unittest

from utils import MoviesTest


class TestPost(MoviesTest):

    def test_post_not_allow(self):
        response = self.app.post('/api_tests/movies/1234', headers=self.headers, data={})
        self.assertEqual(response.status_code, 405)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Not supported resource creation'}, response_json)

    def test_post_empty(self):
        movie = {}
        response = self.app.post('/api_tests/movies', headers=self.headers, data=movie)
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data or '{}')
        self.assertIn('id', response_json)
        self.assertIsNotNone(response_json.get('id'))
        self.assertIn('Location', response.headers)
        self.assertIn('/api_tests/movies/%s' % response_json['id'], response.headers['Location'])
        response = self.app.get(response.headers['Location'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        movie.update({'id': response_json['id']})
        self.assertDictEqual(movie, response_json)

    def test_post(self):
        movie = {'name': u'Kill Bill: Volumen 1', 'year': u'2003'}
        response = self.app.post('/api_tests/movies', headers=self.headers, data=movie)
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data or '{}')
        self.assertIn('id', response_json)
        self.assertIsNotNone(response_json.get('id'))
        self.assertIn('Location', response.headers)
        self.assertIn('/api_tests/movies/%s' % response_json['id'], response.headers['Location'])
        response = self.app.get(response.headers['Location'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        movie.update({'id': response_json['id']})
        self.assertDictEqual(movie, response_json)

    def test_post_and_ignore_id_parameter(self):
        movie = {'name': u'Kill Bill: Volumen 1', 'year': u'2003', 'id': u'1', '_id': u'2'}
        response = self.app.post('/api_tests/movies', headers=self.headers, data=movie)
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data or '{}')
        self.assertNotEqual(response_json.get('id'), movie['id'])
        self.assertNotEqual(response_json.get('id'), movie['_id'])
        self.assertIn('Location', response.headers)
        self.assertIn('/api_tests/movies/%s' % response_json['id'], response.headers['Location'])
        response = self.app.get(response.headers['Location'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        movie.update({'id': response_json['id']})
        movie.pop('_id')
        self.assertDictEqual(movie, response_json)

    def test_post_nested(self):
        star = {'grade': u'10'}
        response = self.app.post(
            '/api_tests/movies/%s/stars' % self.movies[2]['id'],
            headers=self.headers,
            data=star
        )
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data or '{}')
        self.assertIn('id', response_json)
        self.assertIsNotNone(response_json.get('id'))
        self.assertIn('Location', response.headers)
        self.assertIn('/api_tests/stars/%s' % response_json['id'], response.headers['Location'])
        star.update({'id': response_json.get('id')})
        star.update({'movies': [self.movies[2]['id']]})
        response = self.app.get(response.headers['Location'], headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(star, response_json)


if __name__ == '__main__':
    unittest.main()
