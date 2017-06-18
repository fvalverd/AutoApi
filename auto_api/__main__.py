#!/usr/bin/env python

import click
from auto_api import AutoApi


@click.command()
@click.option('--auth', '-a', help='AutoApi with authentication', is_flag=True)
@click.option('--debug', '-d', help='Flask debug mode', is_flag=True)
@click.option('--config', '-f', help='AutoApi config path')
@click.option('--host', '-h', help='AutoApi host', default='0.0.0.0')
@click.option('--port', '-p', help='AutoApi port', default=8686, type=int)
@click.option('--reloader', '-r', help='Use Flask reloader', is_flag=True)
def main(auth, debug, config, host, port, reloader):
    autoapi = AutoApi(auth=auth, config_path=config)
    autoapi.app.run(
        host=host, port=port, use_reloader=reloader, debug=debug, threaded=True
    )


if __name__ == '__main__':
    main()
