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

    movies = [
        {'name': 'Jackie Brown', 'year': '1997'},
        {'name': 'Pulp Fiction', 'year': '1994'},
        {'name': 'Reservoir Dogs', 'year': '1992'},
    ]

    @classmethod
    def setUpClass(cls):
        super(MoviesTest, cls).setUpClass()
        with _admin_manager(cls.app.application) as db:
            db.movies.insert(MoviesTest.movies)
            cls.movies = [format_result(movie) for movie in cls.movies]

    @classmethod
    def tearDownClass(cls):
        with _admin_manager(cls.app.application) as db:
            db.movies.drop()
        super(MoviesTest, cls).tearDownClass()
