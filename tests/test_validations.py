# -*- coding: utf-8 -*-
import json
import datetime

import mock

from auto_api.mongodb import admin, get_client
from . import BaseTest, BaseAuthTest, LoggedTest


class TestApiLimits(BaseAuthTest):

    def test_invalid_api_name(self):
        headers = self.get_admin_headers()
        response = self.app.get('/Movie$', headers=headers)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data or '{}')
        self.assertTrue(response_json['message'].startswith('Api can not contain the following chracters: /\. "$'))


class TestCaseSensitive(BaseAuthTest):

    def test_api_url(self):
        headers = self.get_admin_headers()
        apiL, apiC, apiU = self.api.lower(), self.api.capitalize(), self.api.upper()

        # Create
        response_lowered = self.app.post(apiL+'/movies', headers=headers, content_type='application/json', data=json.dumps({"name": "nameL"}))
        self.assertEqual(response_lowered.status_code, 201)
        response_capitaized = self.app.post(apiC+'/movies', headers=headers, content_type='application/json', data=json.dumps({"name": "nameC"}))
        self.assertEqual(response_capitaized.status_code, 201)
        response_uppered = self.app.post(apiU+'/movies', headers=headers, content_type='application/json', data=json.dumps({"name": "nameU"}))
        self.assertEqual(response_uppered.status_code, 201)

        response_lowered = self.app.get(apiL+'/movies', headers=headers)
        self.assertEqual(response_lowered.status_code, 200)
        response_capitaized = self.app.get(apiC+'/movies', headers=headers)
        self.assertEqual(response_capitaized.status_code, 200)
        response_uppered = self.app.get(apiU+'/movies', headers=headers)
        self.assertEqual(response_uppered.status_code, 200)

        self.assertEqual(response_lowered.data, response_capitaized.data)
        self.assertEqual(response_capitaized.data, response_uppered.data)

    def test_api_param(self):
        # Login with upper-case API name
        response = self.app.post('/login', data={
            'email': self.user,
            'password': self.password,
            'api': self.api.upper(),
        })
        headers = self.response_to_headers(response)

        # Get elements with lower-case API name
        response = self.app.get(self.api.lower()+'/movies', headers=headers)
        self.assertEqual(response.status_code, 200)

        # Logout with capitalize API name
        response = self.app.post('/logout', headers=headers, data={'api': self.api.capitalize()})
        self.assertEqual(response.status_code, 204)


class TestDateTimeData(BaseTest):
    def setUp(self):
        client = get_client(self.autoapi.app)
        client[self.api].dates.drop()

    def test_autoapi_datetime(self):
        collection = 'dates'
        date = datetime.datetime(2019, 4, 14, 18, 30, 5)

        # Create a date
        client = get_client(self.autoapi.app)
        result = client[self.api][collection].insert_one({'date': date})
        client.close()
        oid = str(result.inserted_id)

        path = '/{}/{}/{}'.format(self.api, collection, oid)
        response = self.app.get(path)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertEqual('2019-04-14T18:30:05', response_json.get('date'))


def mocked_delete_token(app, api, user, token):
    with admin(app) as client:
        client[api].command('updateUser', user, customData={})
    from auto_api.mongodb import delete_token
    delete_token(app, api, user, token)


class TestUsersWithoutCustomData(LoggedTest):

    @mock.patch('auto_api.operations.delete_token', mocked_delete_token)
    def test_force_custom_data_be_empty(self):
        response = self.app.post('/login', data={
            'email': self.user,
            'password': self.password,
            'api': self.api,
        })
        headers = self.response_to_headers(response)
        self.app.post('/logout', headers=headers, data={'api': self.api})
