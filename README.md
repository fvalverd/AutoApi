### Run api server
```
./scripts/run_server
```

### Test api server
```
./scripts/run_test
```

#**Config ApiSDF**

sudo apt-get install libffi-dev libssl-devel

## Config file
Fill server.cfg and tests.cfg

## Config MongoDB server
ApiSDF use MongoDB users, so you have to add auth=true to your mongodb.cfg or run mongod with --auth

- http://docs.mongodb.org/manual/core/authentication
- http://docs.mongodb.org/manual/core/authorization


## Config MongoDB admin user

- http://docs.mongodb.org/manual/tutorial/add-user-administrator/
- http://docs.mongodb.org/manual/core/authentication/#localhost-exception

