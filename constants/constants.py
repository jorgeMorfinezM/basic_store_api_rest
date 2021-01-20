# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A19.1 ($Rev: 1 $)"

import yaml
from logger_controller.logger_control import *


logger = configure_ws_logger()


class Constants:

    @staticmethod
    def get_constants_file(self):
        try:
            with open(self, 'r') as ymlfile:
                cfg = yaml.safe_load(ymlfile)

        except yaml.YAMLError as exc:
            logger.error("Error in configuration file: %s", exc)
        except yaml.MarkedYAMLError as mye:
            logger.error('Your settings file(s) contain invalid YAML syntax! '
                         'Please fix and restart!, {}'.format(str(mye)))
            raise yaml.ImproperlyConfigured(
                'Your settings file(s) contain invalid YAML syntax! Please fix and restart!, {}'.format(str(mye))
            )

        return cfg

