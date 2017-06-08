# -*- coding: utf-8 -*-
import json
import unittest

from .. import MoviesTest


class TestDeleteResource(MoviesTest):

    def setUp(self):
        self.setUpClass()
        super(TestDeleteResource, self).setUp()

    def test_delete_invalid_id(self):
        response = self.app.delete('/%s/movies/a1' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 409)
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, json.loads(response.data))

    def test_delete_not_found_id(self):
        response = self.app.delete('/%s/actors/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data)
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[0]['id']},
            response_json
        )

    def test_delete(self):
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        self.assertEqual(response.status_code, 204)
        response_json = self._count_test('movies', 2)
        self.assertNotIn(self.movies[0], response_json.get('items'))

    def test_delete_nested(self):
        response = self.app.delete(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[0]['id'], self.movies[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)
        response_json = self._count_test('movies', 2)
        self.assertNotIn(self.movies[0], response_json.get('items'))


class TestDeleteCollection(MoviesTest):

    def setUp(self):
        self.setUpClass()
        super(TestDeleteCollection, self).setUp()

    def test_delete(self):
        response = self.app.delete('/%s/movies' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 204)
        response_json = self._count_test('movies', 0)
        self.assertEqual([], response_json.get('items'))

    def test_delete_nested(self):
        response = self.app.delete(
            '/%s/actors/%s/movies' % (self.api, self.actors[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)
        response_json = self._count_test('movies', 2)
        self.assertNotIn(self.movies[0], response_json.get('items'))


if __name__ == '__main__':
    unittest.main()
