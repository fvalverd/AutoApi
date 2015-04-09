# -*- coding: utf-8 -*-
import unittest

from ApiSDF import app
from ApiSDF.auth import _admin_manager
from ApiSDF.utils import format_result


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.app = app.test_client()


class MoviesTest(BaseTest):

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
    def setUpClass(cls):
        super(MoviesTest, cls).setUpClass()

        # Fixture
        with _admin_manager(cls.app.application, app.config['APISDF_DB']) as db:
            db.actors.insert(cls.actors)
            cls.actors = [format_result(actor) for actor in cls.actors]
            for movie in cls.movies:
                movie.update({'actors': [cls.actors[cls.movies.index(movie)]['id']]})
            db.movies.insert(cls.movies)
            cls.movies = [format_result(movie) for movie in cls.movies]

        # Login
        response = cls.app.post('/login', data={
            'email': app.config['APISDF_ADMIN'],
            'password': app.config['APISDF_ADMIN_PASS'],
            'api': app.config['APISDF_DB'],
        })
        cls.headers = {
            'X-Email': response.headers['X-Email'],
            'X-Token': response.headers['X-Token']
        }

    @classmethod
    def tearDownClass(cls):
        # Remove fixture
        with _admin_manager(cls.app.application, app.config['APISDF_DB']) as db:
            db.actors.drop()
            db.movies.drop()

        # Logout
        cls.app.post('/logout', headers=cls.headers, data={'api': app.config['APISDF_DB']})

        super(MoviesTest, cls).tearDownClass()
