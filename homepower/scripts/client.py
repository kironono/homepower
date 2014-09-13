# coding: utf-8

import sys
import os
import logging
import json
import serial
import redis
import transaction
import datetime

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from homepower.models import (
    initialize_sql,
    DBSession,
    WattLog,
)

log = logging.getLogger("homepower")


class Client(object):

    def __init__(self, settings):
        self.settings = settings

        serial_port = settings["client.serial_port"]
        baud_rate = settings["client.baud_rate"]
        self.serial = serial.Serial(serial_port, baud_rate)
        log.debug("SerialPort: %s", serial_port)
        log.debug("BaudRate: %s", baud_rate)
        log.debug("isOpen: %s", self.serial.isOpen())

        self.redis = redis.Redis(
            host=settings["redis.host"],
            port=settings["redis.port"],
            db=settings["redis.db"],
            password=settings["redis.password"],
        )
        self.pubsub = self.redis.pubsub()

    def process_data(self, data):
        values = data.strip().split(",")
        if len(values) != 2:
            log.error("invalid data: %s", values)
            return

        now = datetime.datetime.now()
        tick = {
            "current": float(values[0]),
            "watt": float(values[1]),
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        log.debug("data: %s", tick)

        with transaction.manager:
            w = WattLog(
                value=tick["watt"],
                created_at=now,
            )
            DBSession.add(w)

        self.redis.publish("tick", json.dumps(tick))

    def start(self):
        log.info("start client")
        self.serial.flushInput()

        while True:
            read_data = self.serial.readline()
            try:
                self.process_data(read_data)
            except Exception, e:
                log.exception(e)

        self.serial.close()

    def shutdown(self):
        log.debug("shutdown")
        self.serial.close()


def usage(argv):
    cmd = os.path.basename(argv[0])
    print("usage: %s CONFIG-URI" % cmd)
    sys.exit(2)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    initialize_sql(settings)

    client = Client(settings)
    try:
        client.start()
    except KeyboardInterrupt:
        client.shutdown()


if __name__ == "__main__":
    main()
