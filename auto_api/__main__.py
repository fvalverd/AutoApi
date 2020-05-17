#!/usr/bin/env python

import click
from auto_api import AutoApi
from auto_api.mongodb import update_roles, ADMIN_KEYS


@click.group()
def cli():
    pass


@cli.command()
@click.option('--auth', '-a', help='AutoApi with authentication', is_flag=True)
@click.option('--debug', '-d', help='Flask debug mode', is_flag=True)
@click.option('--host', '-h', help='AutoApi host', default='0.0.0.0')
@click.option('--port', '-p', help='AutoApi port', default=8686, type=int)
@click.option('--reloader', '-r', help='Use Flask reloader', is_flag=True)
def run(auth, debug, host, port, reloader):
    autoapi = AutoApi(auth=auth)
    autoapi.run(
        host=host, port=port, use_reloader=reloader, debug=debug, threaded=True
    )


@cli.command()
@click.option('--port', '-p', help='MongoDB port', default=None, type=int)
def update_admin(port):
    autoapi = AutoApi(auth=True, port=port)
    name = autoapi.config[ADMIN_KEYS['name']]
    update_roles(autoapi, api='admin', user=name, roles={'admin': True})


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    cli()
