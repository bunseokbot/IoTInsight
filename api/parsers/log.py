#!/usr/bin/env python
# -*- coding:utf-8 -*-

import util.log_file as log_file

_logger = None


def log():
    global _logger
    if _logger is None:
        _logger = log_file.LocalFileLogger('__analyzer__', 'analyzer.log')

    return _logger

if __name__ == '__main__':
    pass
