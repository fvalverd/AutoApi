#!/usr/bin/env python
import os
import sys

import pytest
from mongobox import MongoBox


MONGO_PORT, MONGO_AUTH_PORT = 27018, 27019


def run(args=None):
    if args is None:
        args = []

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

    # create temporal directory
    TMP_DIR = os.path.join(CURRENT_DIR, '.tmp')
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    DB_PATH = os.path.join(TMP_DIR, 'data')
    DB_PATH_AUTH = os.path.join(TMP_DIR, 'data_auth')

    # set autoapi environment variable for config
    os.environ['AUTOAPI_SETTINGS'] = os.path.join(
        CURRENT_DIR, 'tests.cfg.default'
    )

    mongobox = MongoBox(mongod_bin='mongod', db_path=DB_PATH, port=MONGO_PORT)
    mongoboxA = MongoBox(
        mongod_bin='mongod', auth=True,
        db_path=DB_PATH_AUTH, port=MONGO_AUTH_PORT
    )

    status, statusA = False, False
    errno = 1
    try:
        print "Starting mongo servers:"

        # start server
        print " - server...",
        sys.stdout.flush()
        mongobox.start()
        status = True
        print "OK"

        # start auth server
        print " - server auth...",
        sys.stdout.flush()
        mongoboxA.start()
        print "OK\n"
        statusA = True
        sys.stdout.flush()

        errno = pytest.main(*args)
    finally:
        # stop servers
        if status:
            print "\n\nStoping mongo servers:"
            print " - server...",
            sys.stdout.flush()
            mongobox.stop()
            print "OK"
            if statusA:
                print " - server auth...",
                sys.stdout.flush()
                mongoboxA.stop()
                print "OK"
    return errno


if __name__ == '__main__':
    sys.exit(run())
