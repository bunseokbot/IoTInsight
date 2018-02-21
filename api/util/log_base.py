#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import logging.handlers
import inspect


def deco_log(func):

    def _deco_log(self, msg):
        stack_frames = inspect.stack()
        stack_frame = stack_frames[1]
        prefix = '{0}:{1}, {2}()'.format(
            os.path.basename(stack_frame[1]), stack_frame[2], stack_frame[3])
        decorated_msg = '{0}, {1}'.format(prefix, msg)
        func(self, decorated_msg)

    return _deco_log


class MyRotatingFileHandler(logging.handlers.RotatingFileHandler):

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backupCount > 0:
            for count in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, count)
                dfn = "%s.%d" % (self.baseFilename, count + 1)
                try:
                    if os.path.exists(dfn):
                        os.remove(dfn)
                except Exception as e:
                    print('#1, pid={}, exception={}, remove({})'.format(
                        os.getpid(), e, dfn))
                    raise e
                try:
                    if os.path.exists(sfn):
                        os.rename(sfn, dfn)
                except Exception as e:
                    print('#2, pid={}, exception={}, remove({})'.format(
                        os.getpid(), e, dfn))
                    raise e
                dfn = self.baseFilename + ".1"
                try:
                    if os.path.exists(dfn):
                        os.remove(dfn)
                except Exception as e:
                    print('#3, pid={}, exception={}, remove({})'.format(
                        os.getpid(), e, dfn))
                    raise e
                try:
                    if os.path.exists(self.baseFilename):
                        os.rename(self.baseFilename, dfn)
                except Exception as e:
                    print('#4, pid={}, exception={}, rename({}->{})'.format(
                        os.getpid(), e, self.baseFilename, dfn))
                    raise e
        if not self.delay:
            self.stream = self._open()


class LogBase():

    def __init__(self):
        self._logger = None

        logging._levelToName[logging.DEBUG] = 'DEBUG'
        logging._levelToName[logging.ERROR] = 'ERR '
        logging._levelToName[logging.WARNING] = 'WARN'

    @deco_log
    def debug(self, msg):
        self._logger.debug(msg)

    @deco_log
    def error(self, msg):
        self._logger.error(msg)

    @deco_log
    def info(self, msg):
        self._logger.info(msg)

    @deco_log
    def warn(self, msg):
        self._logger.warn(msg)


if __name__ == "__main__":
    pass
