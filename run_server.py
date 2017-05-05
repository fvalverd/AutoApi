#!/usr/bin/env python
import os

import click
from auto_api import AutoApi


# Set autoapi config
PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'server.cfg'
)


@click.command()
@click.option('--auth', '-a', help='MongoDB auth', default=False, type=bool)
@click.option('--config', '-f', help='AutoApi config path', default=PATH)
def main(auth, config):
    autoapi = AutoApi(auth=auth, config_path=config)
    autoapi.run()


if __name__ == '__main__':
    main()
