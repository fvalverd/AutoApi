# AutoApi

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/auto_api.svg)](https://pypi.org/project/auto-api/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/fvalverd/AutoApi?sort=semver)](https://github.com/fvalverd/AutoApi/releases)
[![PyPI](https://img.shields.io/pypi/v/auto-api)](https://pypi.org/project/auto-api/)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/felipevalverde/autoapi?label=docker&sort=semver)](https://hub.docker.com/r/felipevalverde/autoapi)

[![tests](https://github.com/fvalverd/AutoApi/workflows/tests/badge.svg?branch=master)](https://github.com/fvalverd/AutoApi/actions?query=workflow%3A%22tests%22)
[![Build Status](https://travis-ci.org/fvalverd/AutoApi.svg?branch=master)](https://travis-ci.org/fvalverd/AutoApi?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/fvalverd/AutoApi/badge.svg?branch=master)](https://coveralls.io/github/fvalverd/AutoApi?branch=master)
[![Code Climate](https://codeclimate.com/github/fvalverd/AutoApi/badges/gpa.svg)](https://codeclimate.com/github/fvalverd/AutoApi)

The goal of AutoApi is avoid developing an [API REST](https://en.wikipedia.org/wiki/Representational_state_transfer) at the start of a project, making a prototype easier than usual. AutoApi also has an authentication system and multiple APIs are supported.

## Quickstart

Assuming you have MongoDB server running in *localhost* on the default port *27017* without authentication, AutoApi can be started as following:

##### Docker container
```shell
$ docker run -it -e MONGO_HOST=localhost -e MONGO_PORT=27017 felipevalverde/autoapi:latest
  ...
  Listening at: http://0.0.0.0:8686
```

##### Python module
```shell
$ workon api
(api) $ pip install auto_api
(api) $ MONGO_HOST=localhost MONGO_PORT=27017 python -m auto_api run
  * Running on http://0.0.0.0:8686/ (Press CTRL+C to quit)
  ...
```

A personal agenda is a good example to show how AutoApi works. We will use the *example* API to insert and retrieve items from *agenda* collection.

### Insert
To add an item in the agenda, the following HTTP request shows how to do it:
<pre>
<b>POST</b> http://localhost:8686/example/agenda
<b>Content-Type</b>: application/json

{
  "name": "user",
  "email": "user@email.com",
  "phone": "+123 456-789",
  "address": "123 Street"
}
</pre>
It's important to add **/example** (API name) before the REST path **/agenda**, because that is the way AutoApi identifies them.
The response will contain the id of the created item as:
```
{"id": "591a79400000000000000000"}
```

Where the value of *id* will always be a [MongoDB ObjectId](https://docs.mongodb.com/manual/reference/method/ObjectId).


### Retrieve
To get the previous inserted item in the agenda, is required to know the *id* of the item. The previous response shows the *id* is *591a79400000000000000000*, so the item can be retrieve making the following HTTP request:

<pre>
<b>GET</b> http://localhost:8686/example/agenda/591a79400000000000000000
</pre>
In the same way as the insert operation, the API name and the REST path are required, in this case the path is **/agenda/591a79400000000000000000**. The response will contain the initial inserted data and the AutoApi assigned *id*:
<pre>
{
  "id": "591a79400000000000000000",
  "name": "user",
  "email": "user@email.com",
  "phone": "+123 456-789",
  "address": "123 Street"
}
</pre>

But, if you want to retrieve all the items of the agenda, the following HTTP request shows how:
<pre>
<b>GET</b> http://localhost:8686/example/agenda
</pre>

And the response will be:
<pre>
[
  {
    "id": "591a79400000000000000000",
    "name": "user",
    "email": "user@email.com",
    "phone": "+123 456-789",
    "address": "123 Street"
  },
  ...
]
</pre>


## How does AutoApi work?

AutoApi was develop on [Python](https://www.python.org/) using [Flask](http://flask.pocoo.org/) and [MongoDB](https://www.mongodb.com/), it was thought to support multiples API because AutoApi uses each database to represent each API. This means that to differentiate between two APIs it is necessary to add the API name as a prefix in the URL. For instance, to retrieve all the movies from *imdb-copy* API it is necessary to do a **GET** to **/imdb-copy/movies**, and to retrieve the movies from **rottentomatoes-copy** API the URL is **/rottentomatoes-copy/movies**.

Another important AutoApi's feature is the authentication, but authentication in for this tool is at API level, this means that users can not be shared between APIs. The reason why users can not be shared is because AutoApi uses MongoDB users instead of a collection to store them, so they are strictly related to a database and as AutoApi is considering a database as an API they are isolated per database.

### Configuration

AutoApi uses MongoDB to store all the neccesary data, then it is necessary to know the location of the database, this means that next environment variables **must be provided**: *MONGO_HOST* and *MONGO_PORT*.

In the same way, if authentication is needed, the next environment variables must be provided too: *MONGO_ADMIN* and *MONGO_ADMIN_PASS*.


## **AutoApi features**

### Authentication & Authorization

AutoApi authentication is optional, by default it is not activated. To activate it is necessary:
 - [MongoDB auth](#mongodb) activated
 - [AutoApi admin configurations](#configuration)
 - [Run AutoApi server](running-autoapi) with --auth flag

#### Authentication

Each API has their own users, so users have to logged specifying the API in the request:

<pre>
<b>POST</b> /login
<b>Content-Type</b>: application/json

{
  "api": "example",
  "email": "user@email.com",
  "password": "pass"
}
</pre>

The response will contain a session token in the headers and body:

<pre>
<b>X-Email</b>: user@email.com
<b>X-Token</b>: 123456

{
  "email": "user@email.com",
  "token": "123456"
}
</pre>

To logout, users have to specify the API too:

<pre>
<b>POST</b> /logout
<b>Content-Type</b>: application/json
<b>X-Email</b>: user@email.com
<b>X-Token</b>: 123456

{"api": "example"}
</pre>

#### Users and Authorization

**Only admin users** can create more users specifying the API and CRUD roles:

<pre>
<b>POST</b> /user
<b>Content-Type</b>: application/json
<b>X-Email</b>: ADMIN_USER
<b>X-Token</b>: ADMIN_USER_TOKEN

{
  "email": "other_user@email.com",
  "password": "pass",
  "api": "example",
  "roles": ["read", "update"]
}
</pre>

The last request creates the user *other_user@email.com* and authorizes him to *read* and *update* the *example* API without any API creation request.

Each user can update his own password and only an admin user can change other users password . The change can be done using the following request:
<pre>
<b>POST</b> /password
<b>Content-Type</b>: application/json
<b>X-Email</b>: USER
<b>X-Token</b>: USER_TOKEN

{
  "email": "other_user@email.com",
  "password": "new-pass",
  "api": "example"
}
</pre>

It is important to note that the request needs the *email* parameter to select to user that will change the password.

Finally, only an admin user can change the authorization roles for a particular user using the following request:
<pre>
<b>POST</b> /roles
<b>Content-Type</b>: application/json
<b>X-Email</b>: ADMIN_USER
<b>X-Token</b>: ADMIN_USER_TOKEN

{
  "email": "other_user@email.com",
  "api": "example",
  "roles": {
    "update": false,
    "delete": true
  }
}
</pre>


### Collections and Resources

#### API

To use an API in AutoApi it is not necessary to create it, it is created on demand and there is no operations related for path **/api**.

#### API collection

To use and API collection in AutoApi it is not necessary to create it, it is also created on demand.

#### CRUD collection's resources

It is important to remember that if AutoApi's authentication is enabled then only logged users, with the respective authorization, can CRUD API's resources.

A good API REST example is to show how to mark as a classic all the movies where *actor_1* appears.

<pre>
<b>PATCH</b> /example/actors/actor_1/movies
<b>Content-Type</b>: application/json
<b>X-Email</b>: user@email.com
<b>X-Token</b>: USER_TOKEN

{"classic": true}
</pre>

More info about REST:

- http://www.restapitutorial.com/lessons/httpmethods.html
- http://restful-api-design.readthedocs.org/en/latest/



## Dependencies and configuration

#### Installation

##### Docker container

You can pull the latest docker image as following:

```shell
docker pull felipevalverde/autoapi:latest
```

##### Python module

You can install the latest python module. I strongly recommend you to use [virtualenv](https://virtualenv.pypa.io) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) as following:

```shell
$ workon api
(api) $ pip install auto_api
```


#### MongoDB

AutoApi doesn't required modifications on MongoDB configuration to handle APIs, collectios or resources. But, if you want to activate [Authentication](#authentication) and [Authorization](#authorization), as AutoApi uses MongoDB users, it is necessary to set *auth=true* in your *mongodb.cfg* or run *mongod* with the flag *--auth* and provide the neccesary [AutoApi environment variables](#configuration).

Related info:
- http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
- http://docs.mongodb.org/manual/core/authentication
- http://docs.mongodb.org/manual/core/authorization
- http://docs.mongodb.org/manual/tutorial/add-user-administrator


## Running AutoApi

After [installing AutoApi](#installation) it will be created an executable called **autoapi** and the python module **auto_api**. Also, remember that if you want to run AutoApi with authentication, you must first [turn on the authentication in MongoDB](#mongodb) and then provide the flag **--auth**.

```shell
(api) $ autoapi run [ --auth ]
```

or

```shell
(api) $ python -m auto_api run [ --auth ]
```

## Testing AutoApi

To run the AutoApi test there is a script called *run_tests.py*, that automatically start and stop two MongoDB servers for testing purpose only (one with authentication enabled).

```shell
(api) $ ./run_tests.py
```

or

```shell
(api) $ python setup.py run_tests [ -a '[pytest-parameters]' ]
```
