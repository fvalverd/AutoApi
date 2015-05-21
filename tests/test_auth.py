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


class TestCreateUser(MoviesTest):

    def test_read_role(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['read']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 200)

        # create
        response = self.app.post('/%s/movies' % self.api, headers=headers, data='')
        self.assertEqual(response.status_code, 403)

        # update put
        response = self.app.put('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

        # update patch
        response = self.app.patch('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_create_role(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['create']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 403)

        # update patch
        response = self.app.patch('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_update_role(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['update']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 403)

        # create
        response = self.app.post('/%s/movies' % self.api, headers=headers, data='')
        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 403)

    def test_delete_role(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['delete']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        response = self.app.post('/login', data=test_data)
        self.assertEqual(response.status_code, 200)
        headers = self.response_to_headers(response)

        # read
        response = self.app.get('/%s/movies' % self.api, headers=headers)
        self.assertEqual(response.status_code, 403)

        # create
        response = self.app.post('/%s/movies' % self.api, headers=headers, data='')
        self.assertEqual(response.status_code, 403)

        # update put
        response = self.app.put('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

        # update patch
        response = self.app.patch('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=headers)
        self.assertEqual(response.status_code, 403)

        # delete
        response = self.app.delete('/%s/movies/%s' % (self.api, self.movies[1]['id']), headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_admin_role(self):
        test_data = {'email': u'fvalverd', 'password': u'pass', 'api': self.api, 'roles': ['admin']}

        admin_headers = self.get_admin_headers()
        response = self.app.post(
            '/user',
            headers=admin_headers,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

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


class TestEditRoles(MoviesTest):

    @classmethod
    def setUpClass(cls):
        super(TestEditRoles, cls).setUpClass()
        cls.read_user = {'email': u'fvalverd', 'password': u'pass', 'api': cls.api, 'roles': ['read']}
        cls.app.post(
            '/user',
            headers=cls.headers,
            data=json.dumps(cls.read_user),
            content_type='application/json'
        )
        response = cls.app.post('/login', data=cls.read_user)
        cls.read_user_header = cls.response_to_headers(response)

    def test_edit_read_role(self):
        for read, status_code in [(False, 403), (True, 200)]:
            response = self.app.post(
                '/roles',
                headers=self.headers,
                data=json.dumps({'email': self.read_user['email'], 'api': self.api, 'roles': {'read': read}}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 204)

            response = self.app.get('/%s/movies' % self.api, headers=self.read_user_header)
            self.assertEqual(response.status_code, status_code)

    def test_edit_create_role(self):
        for create, status_code in [(True, 201), (False, 403)]:
            response = self.app.post(
                '/roles',
                headers=self.headers,
                data=json.dumps({'email': self.read_user['email'], 'api': self.api, 'roles': {'create': create}}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 204)

            response = self.app.post(
                '/%s/movies' % self.api,
                headers=self.read_user_header,
                data=json.dumps({}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, status_code)

    def test_edit_update_role(self):
        for update, status_code in [(True, 204), (False, 403)]:
            response = self.app.post(
                '/roles',
                headers=self.headers,
                data=json.dumps({'email': self.read_user['email'], 'api': self.api, 'roles': {'update': update}}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 204)

            response = self.app.put(
                '/%s/movies/%s' % (self.api, self.movies[0]['id']),
                headers=self.read_user_header,
                data=json.dumps({}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, status_code)

    def test_edit_delete_role(self):
        for delete, movie_pos, status_code in [(True, 1, 204), (False, 2, 403)]:
            response = self.app.post(
                '/roles',
                headers=self.headers,
                data=json.dumps({'email': self.read_user['email'], 'api': self.api, 'roles': {'delete': delete}}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 204)

            response = self.app.delete(
                '/%s/movies/%s' % (self.api, self.movies[movie_pos]['id']),
                headers=self.read_user_header,
                data=json.dumps({}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, status_code)

    def test_edit_admin_role(self):
        for admin, email, status_code in [(True, 'user_1', 204), (False, 'user_2', 403)]:
            response = self.app.post(
                '/roles',
                headers=self.headers,
                data=json.dumps({'email': self.read_user['email'], 'api': self.api, 'roles': {'admin': admin}}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 204)

            response = self.app.post(
                '/user',
                headers=self.read_user_header,
                data=json.dumps({'email': email, 'password': u'pass', 'api': self.api}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, status_code)


if __name__ == '__main__':
    unittest.main()
