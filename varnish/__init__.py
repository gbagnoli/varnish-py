#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Giacomo Bagnoli <g.bagnoli@asidev.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
from .utils import setup_logging
from . import api
from .stats import VarnishStats
from .logs import VarnishLogs

__version__ = (0, 0, 0, 'dev', 0)
setup_logging()
__all__ = ['Varnish']
log = logging.getLogger(__name__)


class Varnish(object):

    def __init__(self, name=None, log_level=None):
        self.vd = api.init()
        if log_level:
            log_level = log_level.lower()
            log_method = getattr(log, log_level)
            api.set_diagnostic_function(self.vd, log_method, None)

        #api.open(self.vd, True)

        self._name = name
        if self._name:
            api.access_instance(self.vd, self._name)

    def __del__(self):
        try:
            api.close(self.vd)
            api.delete(self.vd)

        except:
            pass

    def open(self, verbose=False):
        api.open(self.vd, verbose)

    def reopen(self, verbose=False):
        api.open(self.vd, verbose)

    @property
    def name(self):
        return self._name or "default"

    @property
    def stats(self):
        if not hasattr(self, "_stats"):
            self._stats = VarnishStats(self)

        return self._stats

    @property
    def logs(self):
        """ Accessing logs using the same instance used to read stats will
            result in an assertion failure in varnish <= 3.0.2
        """
        if not hasattr(self, '_logs'):
            self._logs = VarnishLogs(self)

        return self._logs
