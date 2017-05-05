# -*- coding: utf-8 -*-
import json
import unittest

from .. import MoviesTest


class TestPatchResource(MoviesTest):

    def test_patch_invalid_id(self):
        response = self.app.patch(
            '/%s/movies/a1' % self.api,
            headers=self.headers,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, json.loads(response.data))

    def test_patch_not_found_id(self):
        response = self.app.patch(
            '/%s/actors/%s' % (self.api, self.movies[0]['id']),
            headers=self.headers,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data)
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[0]['id']},
            response_json
        )

    def test_patch(self):
        self.movies[0]['country'] = 'USA'
        response = self.app.patch(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=self.headers,
            data=json.dumps({'country': 'USA'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        response = self.app.get('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        response_json = json.loads(response.data)
        self.assertEqual(self.movies[0], response_json)

    def test_patch_nested(self):
        self.movies[1]['country'] = 'USA'
        response = self.app.patch(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[1]['id'], self.movies[1]['id']),
            headers=self.headers,
            data=json.dumps({'country': 'USA'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        response = self.app.get('/%s/movies/%s' % (self.api, self.movies[1]['id']), headers=self.headers)
        response_json = json.loads(response.data)
        self.assertEqual(self.movies[1], response_json)


class TestPatchCollection(MoviesTest):

    def test_patch(self):
        response = self.app.patch('/%s/movies' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 405)
        self.assertDictContainsSubset(
            {'message': u'Collections do not support this operation'},
            json.loads(response.data)
        )


if __name__ == '__main__':
    unittest.main()
