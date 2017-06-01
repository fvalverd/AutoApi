#!/usr/bin/env python

import click
from auto_api import AutoApi


@click.command()
@click.option('--auth', '-a', help='AutoApi with authentication', is_flag=True)
@click.option('--config', '-f', help='AutoApi config path')
@click.option('--host', '-h', help='AutoApi host', default='0.0.0.0')
@click.option('--port', '-p', help='AutoApi port', default=8686, type=int)
def main(auth, config, host, port):
    autoapi = AutoApi(auth=auth, config_path=config)
    autoapi.run(host=host, port=port)


if __name__ == '__main__':
    main()
