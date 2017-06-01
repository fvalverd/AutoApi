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


## **How AutoApi works ?**

TODO: based on MongoDB
AutoApi its based on MongoDB

### Structure

TODO: describe /api/collection/resource and /operation

### Configuration file
TODO: configuration file


## **AutoApi features**

### Authentication & Authorization

AutoApi authentication is optional, by default is not activated. To activate it is necessary:
 - [MongoDB auth](#mongodb) activated
 - [AutoApi configuration file](#configuration-file) filled
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

Is important to remember that if AutoApi's authentication is enabled then only logged users can CRUD API's resources, but it depends on the user's roles for authorization.

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

AutoApi doesn't required modifications on MongoDB configuration to handle APIs, collectios or resources. But, if you want to activate [Authentication](#authentication) and [Authorization](#authorization), as AutoApi uses MongoDB users, it is necessary to set *auth=true* in your *mongodb.cfg* or run *mongod* with the flag *--auth*. If MongoDB was started with the authentication flag but doesn't have an admin user, AutoApi will try to create him using the given [configuration file](#configuration-file).

Related info:
- http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
- http://docs.mongodb.org/manual/core/authentication
- http://docs.mongodb.org/manual/core/authorization
- http://docs.mongodb.org/manual/tutorial/add-user-administrator


## Running AutoApi

To run AutoApi server there is a script called *run_server.py*.
If you want to try AutoApi with authentication, you must run the script with the flag *-a* (*--auth*) and create a configuration file based on *server.cfg.default*.

<pre>
$ ./run_server.py [[-a] -f server.cfg]
</pre>

## Testing AutoApi

To run AutoApi test there is a script called *run_tests.py*. This script will automatically start and stop two MongoDB servers (one with authentication enabled) only for testing purpose.

<pre>
$ ./run_tests.py [nose-parameters]
</pre>
