# coding: utf-8

from pyramid.config import Configurator

from .models import initialize_sql


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    initialize_sql(settings)

    config.include('pyramid_tm')
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')

    config.add_route('home', '/')
    config.add_route('api_watt_latest', '/api/watt/latest')
    config.add_route('api_watt_today', '/api/watt/today')
    config.add_route('api_watt_month', '/api/watt/month')
    config.add_route('socket_io', 'socket.io/*remaining')

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.scan()

    return config.make_wsgi_app()
