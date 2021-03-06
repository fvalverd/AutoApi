# -*- coding: utf-8 -*-
import json
import os
import unittest
import sys

from auto_api import AutoApi
from auto_api.mongodb import create_user, admin
from auto_api.utils import fix_id

if sys.version_info >= (3, 0):
    from unittest import mock
else:
    import mock


MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_PORT_AUTH = int(os.environ['MONGO_PORT_AUTH'])


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls, auth=False):
        super(BaseTest, cls).setUpClass()
        cls.api = 'api_tests'
        cls.user = 'user'
        cls.password = 'pass'
        cls.port = MONGO_PORT_AUTH if auth else MONGO_PORT
        cls.autoapi = AutoApi(auth=auth, port=cls.port)
        cls.app = cls.autoapi.test_client()
        if auth:
            cls.remove_user(cls.api, cls.user)
            cls.create_user(cls.api, cls.user, cls.password, ['admin'])

    @classmethod
    def response_to_headers(cls, response):
        return {k: response.headers.get(k) for k in ('X-Email', 'X-Token')}

    @classmethod
    def create_user(cls, api, user, password, roles):
        app = cls.app.application
        create_user(app, api, user, password, roles)

    @classmethod
    def remove_user(cls, api, user):
        with admin(cls.app.application) as client:
            r = client[api].command('usersInfo', {'user': user, 'db': api})
            if r['users']:
                client[api].command('dropUser', user)

    def get_admin_headers(self):
        return self.response_to_headers(
            self.app.post('/login', data=dict(
                email=self.app.application.config['MONGO_ADMIN'],
                password=self.app.application.config['MONGO_ADMIN_PASS'],
                api='admin',
            ))
        )

    def assertDictContainsSubset(self, a, b):
        for key, value in a.items():
            self.assertIn(key, b)
            self.assertEqual(value, b[key])


class BaseAuthTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        super(BaseAuthTest, cls).setUpClass(auth=True)


class LoggedTest(BaseAuthTest):

    @classmethod
    def setUpClass(cls):
        super(LoggedTest, cls).setUpClass()
        response = cls.app.post('/login', data={
            'email': cls.user,
            'password': cls.password,
            'api': cls.api,
        })
        cls.headers = cls.response_to_headers(response)

    @classmethod
    def tearDownClass(cls):
        cls.app.post('/logout', headers=cls.headers, data=dict(api=cls.api))
        super(LoggedTest, cls).tearDownClass()

    def _count_test(self, path, amount):
        response = self.app.get(
            '/{api}/{path}'.format(api=self.api, path=path),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertEqual(amount, response_json.get('total'))
        return response_json


class MoviesTest(LoggedTest):

    actors = [
        {'name': u'Pam Grier', 'gender': u'famele'},
        {'name': u'Samuel Jackson', 'gender': u'male'},
        {'name': u'Harvey Keitel', 'gender': u'male'}
    ]

    movies = [
        {'name': u'Jackie Brown', 'year': u'1997'},
        {'name': u'Pulp Fiction', 'year': u'1994'},
        {'name': u'Reservoir Dogs', 'year': u'1992'},
    ]

    @classmethod
    def _clean_movies_and_actors(cls):
        with admin(cls.app.application) as client:
            client[cls.api].actors.drop()
            client[cls.api].movies.drop()
            client[cls.api].stars.drop()

    @classmethod
    def setUpClass(cls):
        super(MoviesTest, cls).setUpClass()
        cls._clean_movies_and_actors()
        with admin(cls.app.application) as client:
            client[cls.api].actors.insert_many(cls.actors)
            cls.actors = [fix_id(actor) for actor in cls.actors]
            for movie in cls.movies:
                movie.update({
                    'actors': cls.actors[cls.movies.index(movie)]['id']
                })
            client[cls.api].movies.insert_many(cls.movies)
            cls.movies = [fix_id(movie) for movie in cls.movies]

    @classmethod
    def tearDownClass(cls):
        cls._clean_movies_and_actors()
        super(MoviesTest, cls).tearDownClass()
