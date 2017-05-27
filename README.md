# AutoApi

[![Build Status](https://travis-ci.org/fvalverd/AutoApi.svg?branch=master)](https://travis-ci.org/fvalverd/AutoApi) [![Coverage Status](https://coveralls.io/repos/fvalverd/AutoApi/badge.svg)](https://coveralls.io/r/fvalverd/AutoApi) [![Code Climate](https://codeclimate.com/github/fvalverd/AutoApi/badges/gpa.svg)](https://codeclimate.com/github/fvalverd/AutoApi)

The goal of AutoApi is avoid developing an API REST at the start of a project, making a prototype easier than usual. AutoApi also has an authentication system and multiple APIs are supported.

## **Quickstart**

Assuming you have MongoDB server running in *localhost* on the default port without authentication, AutoApi starts as:

```shell
$ ./run_server.py
  * Running on http://localhost:8686/ (Press CTRL+C to quit)
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
To get the previous inserted item in the agenda, is required to know the *id* of the item. The previous response show the *id* is *591a79400000000000000000* so the item can be retrieve making the following HTTP request:

<pre>
<b>GET</b> http://localhost:8686/example/agenda/591a79400000000000000000
</pre>
In the same way as the insert operation, the API name and the REST path are required, in this case the path is **/agenda/591a79400000000000000000**
The response will contain the initial inserted data and the AutoApi assigned *id*:
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
    "name": "user",
    "email": "user@email.com",
    "phone": "+123 456-789",
    "address": "123 Street"
  },
  ...
]
</pre>


## **How it works ?**

TODO: based on MongoDB
AutoApi its based on MongoDB

### Structure

TODO: describe /api/collection/resource and /operation


## **How to use it ?**

### Authentication & Authorization

TODO: mention that authentication is optional

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

#### Users

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

The last request create the user *other_user@email.com* and authorize him to *read* and *update* the *example* API without any API creation request.

#### Authorization

TODO: edit roles
TODO: edit password


### Collections and Resources

#### API

AutoApi doesn't need to create an API to use it.
TODO: no additional operations on API

#### API collection

AutoApi doesn't need to create a collection to use it.
TODO: no additional operations on API collection

#### CRUD collection's resource

Is important to remember if AutoApi's authentication is enabled, only logged users can CRUD API's resources, but it depends on the user's roles for authorization.
A read operation will be like this:

<pre>
<b>GET</b> /example/actors/actor_1/movies
<b>X-Email</b>: user@email.com
<b>X-Token</b>: USER_TOKEN
</pre>

The response will contain all *movies*'s resources where actor *actor_1* is present in the *example* API:

<pre>
[
  {"name": "Movie 1", "year": "2014"},
  {"name": "Movie 2", "year": "2013"},
  ...
  {"name": "Movie n", "year": "2000"},
]
</pre>


More info about REST:

- http://www.restapitutorial.com/lessons/httpmethods.html
- http://restful-api-design.readthedocs.org/en/latest/



## **Dependencies and configuration**

#### OpenSSL Ubuntu dependencies

<pre>
$ sudo apt-get install libffi-dev libssl-dev
</pre>

#### Python dependencies

I strongly recommend you to use [virtualenv](https://virtualenv.pypa.io) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io).

<pre>
$ workon autoapi
(autoapi) $ python setup.py develop
</pre>

#### MongoDB

TODO: no additional configuration
TODO: only if authentication is enabled...

AutoApi use MongoDB 3.X users, so you have to set *auth=true* in your *mongodb.cfg* or run *mongod* with the flag *--auth*. If MongoDB was started with the authentication flag but doesn't have an admin user, AutoApi will try to create him using the given config file (see Develop section and Run AutoApi details).

Related info:
- http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
- http://docs.mongodb.org/manual/core/authentication
- http://docs.mongodb.org/manual/core/authorization
- http://docs.mongodb.org/manual/tutorial/add-user-administrator


## Running AutoApi

To run AutoApi server there is a script called *run_server.py*.
If you want to try AutoApi with authentication, you must run the script with the flag *-a* (*--auth*) and create a config file based on *server.cfg.default*.

<pre>
$ ./run_server.py [[-a] -f server.cfg]
</pre>

## Testing AutoApi

To run AutoApi test there is a script called *run_tests.py*. This script will automatically start and stop two MongoDB servers (one with authentication enabled) only for testing purpose.

<pre>
$ ./run_tests.py [nose-parameters]
</pre>
