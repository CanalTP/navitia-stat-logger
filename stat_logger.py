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
import os
import re
from stat_logger.daemon import Daemon

def main():
    """
        main: ce charge d'interpreter les parametres de la ligne de commande
    """
    parser = argparse.ArgumentParser(description="This service logs stat messages from Navitia 2 to file in JSON format")
    parser.add_argument('config_file', type=str)

    #Include environment variables into config file using <%= ENV['YOUR_VAR'] %> pattern
    pattern = re.compile('^(.*)\<%= ENV\[\'(.*)\'\] %\>(.*)$')

    yaml.add_implicit_resolver("!pathex", pattern)

    def pathex_constructor(loader, node):
        value = loader.construct_scalar(node)
        beginVal, envVar, endVal = pattern.match(value).groups()
        if envVar not in os.environ:
            print "Environment variable {0:s} should be defined".format(envVar)
            sys.exit(1)
        return beginVal + os.environ[envVar] + endVal

    yaml.add_constructor('!pathex', pathex_constructor)


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
