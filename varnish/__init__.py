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

from .utils import setup_logging
from . import api
from .stats import VarnishStats

__version__ = (0, 0, 0, 'dev', 0)
setup_logging()
__all__ = ['Varnish']


class Varnish(object):

    def __init__(self, name=None):
        self.vd = api.init()
        self.name = name
        self._stats_init = False
        self._logs_init = False
        if name:
            api.access_instance(self.vd, self.name)

    def __del__(self):
        try:
            api.close(self.vd)
            api.delete(self.vd)

        except:
            pass

    def init_logs(self):
        if self._logs_init:
            return

        api.logs.init(self.vd)
        self._logs_init = True

    def init_stats(self):
        if self._stats_init:
            return

        api.stats.init(self.vd)
        self._stats_init = True

    def read_stats(self):
        self.init_stats()
        stats = list()
        api.stats.iterate(self.vd,
                          lambda point, data: data.append(point), stats)
        return VarnishStats(stats)

    def read_logs(self, source=None):
        def cb(chunk):
            print chunk

        self.init_logs()
        if not source is None:
            raise NotImplementedError

        api.logs.dispatch(self.vd, cb)
