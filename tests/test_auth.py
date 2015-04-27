# -*- coding: utf-8 -*-
import json
import unittest

from tests import BaseTest, MoviesTest


class TestLogin(BaseTest):

    def test_unauthorized(self):
        for verb in [self.app.get, self.app.post, self.app.put, self.app.patch, self.app.delete]:
            response = verb('/%s/movies' % self.api)
            self.assertEqual(response.status_code, 401)
            response_json = json.loads(response.data or '{}')
            self.assertDictEqual(
                response_json,
                {'message': u'You must be logged in "%s" api' % self.api}
            )

    def test_incomplete_login(self):
        data = {'password': self.password}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Invalid email/password/api'}, response_json)

    def test_login_bad_pass(self):
        data = {'email': self.user, 'password': 'bad_pass', 'api': self.api}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Invalid email/password/api'}, response_json)

    def test_login(self):
        data = {'email': self.user, 'password': self.password, 'api': self.api}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 200)


class TestLogout(BaseTest):

    def test_logout(self):
        data = {'email': self.user, 'password': self.password, 'api': self.api}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)
        response = self.app.post('/logout', headers=headers, data={'api': 'api_tests'})
        self.assertEqual(response.status_code, 204)

    def test_login_but_unauthorized_in_other_api(self):
        data = {'email': self.user, 'password': self.password, 'api': self.api}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)
        response = self.app.get('/bad_api/movies', headers=headers)
        self.assertEqual(response.status_code, 401)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(
            response_json,
            {'message': u'You must be logged in "%s" api' % u'bad_api'}
        )

    def test_logout_but_unauthorized_in_other_api(self):
        data = {'email': self.user, 'password': self.password, 'api': self.api}
        response = self.app.post('/login', data=data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)
        response = self.app.post('/logout', headers=headers, data={'api': 'bad_api'})
        self.assertEqual(response.status_code, 401)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(
            response_json,
            {'message': u'You must be logged in "%s" api' % u'bad_api'}
        )


class TestUsers(MoviesTest):

    def test_create_read_user(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['read']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/create_user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 200)

        # create
        response = self.app.post('/%s/movies' % self.api, headers=headers, data='')
        self.assertEqual(response.status_code, 401)

        # update put
        response = self.app.put('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

        # update patch
        response = self.app.patch('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_create_create_user(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['create']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/create_user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 401)

        # create
        response = self.app.post(
            '/%s/movies' % self.api,
            headers=headers,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        # update put
        response = self.app.put('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

        # update patch
        response = self.app.patch('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_create_update_user(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['update']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/create_user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 401)

        # create
        response = self.app.post('/%s/movies' % self.api, headers=headers, data='')
        self.assertEqual(response.status_code, 401)

        # update put
        response = self.app.put(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=headers,
            content_type='application/json',
            data=json.dumps({'field': 'value'})
        )
        self.assertEqual(response.status_code, 204)

        # update patch
        response = self.app.patch(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=headers,
            content_type='application/json',
            data=json.dumps({'another_field': 'value'})
        )
        self.assertEqual(response.status_code, 204)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_create_delete_user(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['delete']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/create_user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 401)

        # create
        response = self.app.post('/%s/movies' % self.api, headers=headers, data='')
        self.assertEqual(response.status_code, 401)

        # update put
        response = self.app.put('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

        # update patch
        response = self.app.patch('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 401)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[1]['id']), headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_create_admin_user(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['admin']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/create_user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 200)

        # create
        response = self.app.post(
            '/%s/movies' % self.api,
            headers=headers,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        # update put
        response = self.app.put(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=headers,
            content_type='application/json',
            data=json.dumps({'field': 'value'})
        )
        self.assertEqual(response.status_code, 204)

        # update patch
        response = self.app.patch(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=headers,
            content_type='application/json',
            data=json.dumps({'another_field': 'value'})
        )
        self.assertEqual(response.status_code, 204)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[2]['id']), headers=headers)
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()
