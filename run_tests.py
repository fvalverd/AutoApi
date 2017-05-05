#!/usr/bin/env python
import os
import sys

from nose import main
from mongobox import MongoBox

from auto_api.config import AUTOAPI_SETTINGS_VAR
from tests import MONGO_PORT, MONGO_AUTH_PORT


if __name__ == '__main__':
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

    # create temporal directory
    TMP_DIR = os.path.join(CURRENT_DIR, 'tmp')
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    DB_PATH = os.path.join(TMP_DIR, 'data')
    DB_PATH_AUTH = os.path.join(TMP_DIR, 'data_auth')

    # set autoapi environment variable for config
    os.environ[AUTOAPI_SETTINGS_VAR] = os.path.join(CURRENT_DIR, 'tests.cfg.default')

    mongobox = MongoBox(mongod_bin='mongod', db_path=DB_PATH, port=MONGO_PORT)
    mongoboxA = MongoBox(mongod_bin='mongod', auth=True, db_path=DB_PATH_AUTH, port=MONGO_AUTH_PORT)

    try:
        print "Starting mongo servers:"

        # start server
        print " - server without auth...",
        sys.stdout.flush()
        mongobox.start()
        print "OK"

        # start auth server
        print " - server with auth...",
        sys.stdout.flush()
        mongoboxA.start()
        print "OK\n"
        sys.stdout.flush()

        # run tests with nose
        main()
    finally:
        # stop servers
        print "\n\nStoping mongo servers:"
        print " - server without auth...",
        sys.stdout.flush()
        mongobox.stop()
        print "OK"
        print " - server with auth...",
        sys.stdout.flush()
        mongoboxA.stop()
        print "OK"
