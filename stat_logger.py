#!/usr/bin/env python
# encoding: utf-8

"""
    This service logs stat messages from Navitia 2 to file in JSON format
"""

import sys
import argparse
import yaml
from exceptions import KeyboardInterrupt
import logging
from stat_logger.daemon import Daemon

def main():
    """
        main: ce charge d'interpreter les parametres de la ligne de commande
    """
    parser = argparse.ArgumentParser(description="This service logs stat messages from Navitia 2 to file in JSON format")
    parser.add_argument('config_file', type=str)
    config_file = ""
    try:
        args = parser.parse_args()
        config_file = args.config_file
    except argparse.ArgumentTypeError:
        print("Bad usage, learn how to use me with %s -h" % sys.argv[0])
        sys.exit(1)

    # Configuration parsing
    with file(config_file, 'r') as stream:
        config = yaml.load(stream)

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
