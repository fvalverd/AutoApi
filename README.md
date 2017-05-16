AutoApi
=======
[![Build Status](https://travis-ci.org/fvalverd/AutoApi.svg?branch=master)](https://travis-ci.org/fvalverd/AutoApi) [![Coverage Status](https://coveralls.io/repos/fvalverd/AutoApi/badge.svg)](https://coveralls.io/r/fvalverd/AutoApi) [![Code Climate](https://codeclimate.com/github/fvalverd/AutoApi/badges/gpa.svg)](https://codeclimate.com/github/fvalverd/AutoApi)

The goal of AutoApi is avoid developing an API REST at the start of a project, making a prototype easier than usual. AutoApi also has an authentication system and multiple APIs are supported.


# **Quickstart**
TODO: add quickstart

# **How it works ?**
## Structure ##
TODO: describe /api/collection/resource and /operation
TODO: mention that authentication is optional

# **How to use it ?**

## Authentication ##

### Login and logout ###
Each API has their own users, so users have to logged specifying the API in the request:
```
POST /login

Content-Type: application/json

{"email": "user@email.com", "password": "pass", "api": "example"}
```
The response will contain a session token in the headers and body:
```
Content-Type: application/json
X-Email: user@email.com
X-Token: 123456

{"email": "user@email.com", "token": "123456"}
```

To logout, users have to specify the API too:
```
POST /logout

Content-Type: application/json
X-Email: user@email.com
X-Token: 123456

{"api": "example"}
```

### Users ###
**Only admin users** can create more users specifying the API and CRUD roles:
```
POST /user

Content-Type: application/json
X-Email: ADMIN_USER
X-Token: ADMIN_USER_TOKEN

{"email": "other_user@email.com", "password": "pass", "api": "example", "roles": ["read", "update"]}
```
The last request create the user *other_user@email.com* and authorize him to *read* and *update* the *example* API without any API creation request.

### Authorization ###
TODO: edit roles
TODO: edit password


## Collections and Resources ##

### API ###
AutoApi doesn't need to create an API to use it.
TODO: no additional operations on API

### API collection ###
AutoApi doesn't need to create a collection to use it.
TODO: no additional operations on API collection

### CRUD collection's resource ###
Is important to remember if AutoApi's authentication is enabled, only logged users can CRUD API's resources, but it depends on the user's roles for authorization.
A read operation will be like this:
```
GET /example/actors/actor_1/movies

Content-Type: application/json
X-Email: user@email.com
X-Token: USER_TOKEN
```

The response will contain all *movies*'s resources where actor *actor_1* is present in the *example* API:

```
Content-Type: application/json

[
  {"name": "Movie 1", "year": "2014"},
  {"name": "Movie 2", "year": "2013"},
  ...
  {"name": "Movie n", "year": "2000"},
]
```


More info about REST:

- http://www.restapitutorial.com/lessons/httpmethods.html
- http://restful-api-design.readthedocs.org/en/latest/



# **Dependencies and configuration**

### OpenSSL Ubuntu dependencies
```
sudo apt-get install libffi-dev libssl-dev
```

### Python dependencies
I strongly recommend you to use [virtualenv](https://virtualenv.pypa.io) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io).
```
workon autoapi
python setup.py develop
```

### MongoDB
TODO: no additional configuration
TODO: only if authentication is enabled...
AutoApi use MongoDB 3.X users, so you have to set *auth=true* in your *mongodb.cfg* or run *mongod* with the flag *--auth*. If MongoDB was started with the authentication flag but doesn't have an admin user, AutoApi will try to create him using the given config file (see Develop section and Run AutoApi details).

Related info:
- http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
- http://docs.mongodb.org/manual/core/authentication
- http://docs.mongodb.org/manual/core/authorization
- http://docs.mongodb.org/manual/tutorial/add-user-administrator


# Running AutoApi
To run AutoApi server there is a script called *run_server.py*.
If you want to try AutoApi with authentication, you must run the script with the flag *-a* (*--auth*) and create a config file based on *server.cfg.default*.
```
./run_server.py [[-a] -f server.cfg]
```

# Testing AutoApi
To run AutoApi test there is a script called *run_tests.py*. This script will automatically start and stop two MongoDB servers (one with authentication enabled) only for testing purpose.
```
./run_tests.py [nose-parameters]
```
