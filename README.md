AutoApi
=======
[![Build Status](https://travis-ci.org/fvalverd/AutoApi.svg?branch=master)](https://travis-ci.org/fvalverd/AutoApi) [![Coverage Status](https://coveralls.io/repos/fvalverd/AutoApi/badge.svg)](https://coveralls.io/r/fvalverd/AutoApi) [![Code Climate](https://codeclimate.com/github/fvalverd/AutoApi/badges/gpa.svg)](https://codeclimate.com/github/fvalverd/AutoApi)

AutoApi was created to not wasting time to developing an API REST at the project start. Has an authentication system to provided secure data and the support for multiple APIs.

### Authentication ###
Each API has their own users, so users have to logged specifying the API like this:
```
POST /login

Content-Type: application/json

{"email": "user@email.com", "password": "pass", "api": "example"}
```
This returns a session token in the headers and body:
```
Content-Type: application/json
X-Email: user@email.com
X-Token: 123456

{"email": "user@email.com", "token": "123456"}
```

To logout, users have to specify the API like this:
```
POST /logout

Content-Type: application/json
X-Email: ADMIN_USER
X-Token: ADMIN_USER_TOKEN

{"api": "example"}
```

### Create user ###
Each API has their own users, so an admin user has to create it specifying the API and CRUD roles like this:
```
POST /create_user

Content-Type: application/json
X-Email: ADMIN_USER
X-Token: ADMIN_USER_TOKEN

{"email": "user@email.com", "password": "pass", "api": "example", "roles": ["read", "update"]}
```
This automatically permit to the user "user@email.com" use the API called "example" without any creation request.

### Create API ###
Is automatic from user creation.

### Create API collection ###
Is automatic from api creation.

### CRUD collection's resource ###
Only logged users could read/create/update/delete API resources. A read example:
```
GET /example/actors/1/movies

Content-Type: application/json
X-Email: user@email.com
X-Token: USER_TOKEN
```

This returns all movies where actor 1 is present in the "example" API like this:

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


#**Config**
### OpenSSL Ubuntu dependencies
```
sudo apt-get install libffi-dev libssl-dev
```

### MongoDB
AutoApi use MongoDB 3.X users, so you have to add auth=true to your mongodb.cfg or run mongod with --auth. If MongoDB does not have admin user, AutoApi will create it from tests.cfg or server.cfg data

Related info:

- http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
- http://docs.mongodb.org/manual/core/authentication
- http://docs.mongodb.org/manual/core/authorization
- http://docs.mongodb.org/manual/tutorial/add-user-administrator


#**Develop**

### Run api server
```
cp server.cfg.default server.cfg
./run_server
```

### Test api server
```
cp tests.cfg.default tests.cfg
./run_test -s
```

#**TODO**
- ~~GET options (filter, sort and skip)~~
- Custom roles
