# -*- coding: utf-8 -*-
import datetime
import json
from operator import itemgetter
import unittest

from bson.objectid import ObjectId

from auto_api.mongodb import admin
from .. import BaseTest, MoviesTest


class TestGetResource(MoviesTest):

    def test_get_not_created(self):
        response = self.app.get('/%s/actors/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[0]['id']},
            response_json
        )

    def test_get_invalid_id(self):
        response = self.app.get('/%s/movies/a1' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 409)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, response_json)

    def test_get(self):
        response = self.app.get('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
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


class TestAutoApiDumps(BaseTest):

    @classmethod
    def setUpClass(cls, auth=False):
        super(TestAutoApiDumps, cls).setUpClass()
        cls.collection = 'movies_with_data'
        cls.now = datetime.datetime(2017, 6, 18, 17, 27, 0)
        cls.oid = ObjectId()
        with admin(cls.app.application) as client:
            cls.oid_oid = str(client[cls.api][cls.collection].insert({
                'oid': cls.oid
            }))
            cls.oid_date = str(client[cls.api][cls.collection].insert({
                'date': cls.now
            }))

    @classmethod
    def tearDownClass(cls):
        with admin(cls.app.application) as client:
            client[cls.api][cls.collection].drop()
        super(TestAutoApiDumps, cls).tearDownClass()

    def test_data_with_object_ids_not_saved_from_autoapi(self):
        response = self.app.get("{}/{}/{}".format(self.api, self.collection, self.oid_oid))
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'oid': str(self.oid)}, response_json)

    def test_data_with_dates_not_saved_from_autoapi(self):
        response = self.app.get("{}/{}/{}".format(self.api, self.collection, self.oid_date))
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'date': self.now.isoformat()}, response_json)


class TestGetCollection(MoviesTest):

    def test_get_not_created(self):
        response = self.app.get('/%s/countries' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': 0, 'items': []}, response_json)

    def test_get(self):
        response = self.app.get('/%s/movies' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': len(self.movies), 'items': self.movies}, response_json)

    def test_get_nested(self):
        response = self.app.get(
            '/%s/actors/%s/movies' % (self.api, self.actors[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': 1, 'items': [self.movies[0]]}, response_json)


class TestGetCollectionParameters(MoviesTest):

    def test_fiilter(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'name': u'Pulp Fiction', 'year': u'1994'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': len(self.movies[1:2]), 'items': self.movies[1:2]}, response_json)

    def test_sort(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_sort': 'year'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertEqual(len(self.movies), response_json.get('total'))
        response_movies = response_json.get('items')
        movies = sorted(self.movies, key=itemgetter('year'))
        for pos in range(len(movies)):
            self.assertEqual(movies[pos], response_movies[pos])

        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_sort': '-year'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        movies.reverse()
        self.assertEqual(len(self.movies), response_json.get('total'))
        response_movies = response_json.get('items')
        for pos in range(len(movies)):
            self.assertEqual(movies[pos], response_movies[pos])

    def test_limit(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_limit': 2}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': len(self.movies[:2]), 'items': self.movies[:2]}, response_json)

    def test_skip(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_skip': 1}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': len(self.movies[1:]), 'items': self.movies[1:]}, response_json)

    def test_regex(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'name': u'Fiction', '_regex': u'name'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': len(self.movies[1:2]), 'items': self.movies[1:2]}, response_json)

    def test_regex2(self):
        response = self.app.get(
            '/%s/actors' % self.api,
            headers=self.headers,
            query_string={'name': u'.*am.*', '_regex': u'name'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual({'total': len(self.actors[0:2]), 'items': self.actors[0:2]}, response_json)


if __name__ == '__main__':
    unittest.main()
