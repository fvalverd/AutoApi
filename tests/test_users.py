# -*- coding: utf-8 -*-
import json
import unittest

from utils import LoggedTest


class TestUsers(LoggedTest):

    def test_create_user_on_created_api(self):
        response = self.app.post('/login', data={
            'email': self.app.application.config['MONGO_ADMIN'],
            'password': self.app.application.config['MONGO_ADMIN_PASS'],
            'api': 'admin',
        })
        self.assertEqual(response.status_code, 200)
        headers = {
            'X-Email': response.headers['X-Email'],
            'X-Token': response.headers['X-Token']
        }
        data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api}
        response = self.app.post('/create_user', headers=headers, data=data)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/login', data=data)
        headers = {
            'X-Email': response.headers['X-Email'],
            'X-Token': response.headers['X-Token']
        }
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 200)
