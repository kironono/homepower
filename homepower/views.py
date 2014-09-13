# coding: utf-8

import logging
import datetime
import redis
import json

from sqlalchemy import func
from pyramid.view import view_config
from socketio import socketio_manage
from socketio.namespace import BaseNamespace

from .models import (
    DBSession,
    WattLog,
)

log = logging.getLogger("homepower")


class TickNamespace(BaseNamespace):

    def listener(self):
        settings = self.request.registry.settings
        r = redis.StrictRedis(
            host=settings["redis.host"],
            port=settings["redis.port"],
            db=settings["redis.db"],
            password=settings["redis.password"],
        )
        pubsub = r.pubsub()
        pubsub.subscribe("tick")

        for m in pubsub.listen():
            if m["type"] == "message":
                data = json.loads(m["data"])
                log.debug("data: %s", data)
                self.emit("tick", data)

    def on_subscribe(self, *args, **kwargs):
        log.debug("subscribe")
        self.spawn(self.listener)


@view_config(
    route_name='home',
    renderer='index.jinja2',
)
def home_view(request):
    return {}


@view_config(
    route_name='api_watt_latest',
    renderer='json',
)
def api_watt_latest_view(request):
    d = DBSession.query(WattLog) \
        .order_by(WattLog.created_at.desc()) \
        .first()
    return {
        "watt": d.value,
        "date": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


@view_config(
    route_name='api_watt_today',
    renderer='json',
)
def api_watt_today_view(request):
    start = datetime.datetime.now() - datetime.timedelta(1)
    query = DBSession.query(
        func.sum(WattLog.value).label("value"),
        func.count(WattLog.value).label("count"),
    )
    query = query.filter(WattLog.created_at > start)
    query = query.group_by(
        func.year(WattLog.created_at),
        func.month(WattLog.created_at),
        func.day(WattLog.created_at),
        func.hour(WattLog.created_at),
    )
    ret = 0
    for d in query.all():
        avg = d.value / d.count
        ret += avg

    return {
        "watt": ret,
    }


@view_config(
    route_name='api_watt_month',
    renderer='json',
)
def api_watt_month_view(request):
    start = datetime.datetime.now() - datetime.timedelta(30)
    query = DBSession.query(
        func.sum(WattLog.value).label("value"),
        func.count(WattLog.value).label("count"),
    )
    query = query.filter(WattLog.created_at > start)
    query = query.group_by(
        func.year(WattLog.created_at),
        func.month(WattLog.created_at),
        func.day(WattLog.created_at),
        func.hour(WattLog.created_at),
    )
    ret = 0
    for d in query.all():
        avg = d.value / d.count
        ret += avg

    return {
        "watt": ret,
    }


@view_config(
    route_name='socket_io',
)
def socketio_service(request):
    retval = socketio_manage(request.environ, {
        '': TickNamespace,
    }, request=request)

    return retval
