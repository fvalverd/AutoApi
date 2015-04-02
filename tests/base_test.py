# -*- coding: utf-8 -*-
import unittest

from ApiSDF import app


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.app = app.test_client()
