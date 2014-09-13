# coding: utf-8

from pyramid.paster import (
    get_app,
    setup_logging,
)
from socketio.server import SocketIOServer
from gevent import monkey

monkey.patch_all()

if __name__ == '__main__':

    config_uri = "development.ini"
    app = get_app(config_uri)
    setup_logging(config_uri)

    print 'Listening on port http://0.0.0.0:8080 and on port 10843 (flash policy server)'

    SocketIOServer(
        ('0.0.0.0', 8080), app,
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 18843),
    ).serve_forever()
