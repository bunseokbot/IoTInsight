#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import logging.handlers
from .log_base import LogBase, MyRotatingFileHandler


class LocalFileLogger(LogBase):

    def __init__(self, logger_name, log_file_name):
        super(LogBase, self).__init__()
        self._logger = logging.getLogger(logger_name)
        if not self._logger.handlers:
            self._strm_handler = logging.StreamHandler()
            self._file_handler = None
            try:
                self._file_handler = MyRotatingFileHandler(
                    log_file_name, maxBytes=(1024 * 1024 * 10), backupCount=20)
            except:
                raise IOError(
                    "Couldn't create/open file {0}. Check permissions.".format(
                        log_file_name))

            self._formatter = logging.Formatter(
                '%(asctime)s, %(levelname)s, %(message)s')

            self._strm_handler.setFormatter(self._formatter)
            self._file_handler.setFormatter(self._formatter)

            self._logger.addHandler(self._strm_handler)
            self._logger.addHandler(self._file_handler)

            self._logger.setLevel(logging.DEBUG)

            self._logger.propagate = False

    def __del__(self):
        logging.shutdown()


if __name__ == "__main__":
    pass
