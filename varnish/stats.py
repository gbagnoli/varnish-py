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

import collections
import datetime


class VarnishStats(collections.Mapping):
    def __init__(self, points):
        object.__setattr__(self, "timestamp", datetime.datetime.utcnow())
        object.__setattr__(self, "_points", {})
        for point in points:
            self._points[point.full_name] = point

    def __getitem__(self, key):
        return self._points[key]

    def __iter__(self):
        return iter(self._points)

    def __len__(self):
        return len(self._points)

    def __contains__(self, obj):
        return obj in self._points

    def __str__(self):
        return "<VarnishStats[%s] - %s elements>" % (self.timestamp, len(self))

    def __repr__(self):
        return "<VarnishStats[%s] - %s" % (self.timestamp, self._points)

    def __setattr__(self, attr, value):
        raise TypeError("VarnishStats' object does not support "
                        "attribute assignment")
