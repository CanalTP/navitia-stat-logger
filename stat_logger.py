#!/usr/bin/env python
# encoding: utf-8

"""
    This service logs stat messages from Navitia 2 to file in JSON format
"""

import sys
from builtins import KeyboardInterrupt
import logging
from stat_logger_conf import config
from stat_logger.daemon import Daemon

def main():
    """
        main: ce charge d'interpreter les parametres de la ligne de commande
    """

    try:
        daemon = Daemon(config)
        daemon.run()
    except KeyboardInterrupt:
        pass
    except:
        logging.exception('fatal error')
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
