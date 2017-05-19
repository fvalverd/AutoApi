#!/usr/bin/env python
import os

import click
from auto_api import AutoApi


PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'server.cfg')


@click.command()
@click.option('--auth', '-a', help='AutoApi with authentication', is_flag=True)
@click.option('--config', '-f', help='AutoApi config path', default=PATH)
@click.option('--host', '-h', help='AutoApi host', default='0.0.0.0')
@click.option('--port', '-p', help='AutoApi port', default=8686, type=int)
def main(auth, config, host, port):
    autoapi = AutoApi(auth=auth, config_path=config)
    autoapi.run(host=host, port=port)


if __name__ == '__main__':
    main()
