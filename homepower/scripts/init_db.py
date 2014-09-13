# coding: utf-8

import sys
import os

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from homepower.models import (
    initialize_sql,
    Base,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s CONFIG-URI' % cmd)
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    initialize_sql(settings)

    Base.metadata.create_all()


if __name__ == '__main__':
    main()
