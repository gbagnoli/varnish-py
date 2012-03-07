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
import inspect
from .api import logs


class VarnishLogs(object):

    def __init__(self, varnish):
        self.varnish = varnish
        self.vd = varnish.vd
        logs.init(self.vd, True)

    def read(self, callback=None):
        if callback:
            args = len(inspect.getargspec(callback).args)

        def wrapper(chunk, priv):
            if callback and args == 0:
                callback()

            elif callback:
                callback(chunk)

        if hasattr(self, 'source'):
            raise NotImplemented

        logs.dispatch(self.vd, wrapper)

    def readline(self, callback):
        def cb(chunk):
            line = LogLine(chunk.fd)
            if line.add_chunk(chunk):
                callback(line)

        self.read(callback=cb)

    def __str__(self):
        return "<%s [instance: %s]>" % (self.__class__.__name__,
                                        self.varnish.name)

    def __repr__(self):
        return str(self)


class LogLine(object):
    _lines = {}

    def __new__(cls, fd):

        if fd in cls._lines and isinstance(cls._lines[fd], LogLine):
            return cls._lines[fd]

        obj = super(LogLine, cls).__new__(cls)
        obj.fd = fd
        obj.chunks = []
        obj.active = False
        obj.complete = False
        if fd in cls._lines:
            # fs is still in _lines, special case for "new but start active"
            # usend on backendreuse
            obj.active = True

        cls._lines[fd] = obj
        return obj

    def add_chunk(self, chunk):

        if self.fd == 0:
            return False

        if not self.active and \
            ((chunk.client and chunk.tag.name == 'reqstart') or
             (chunk.backend and chunk.tag.name == 'backendopen')):
            self.active = True

        elif not self.active:
            return False

        if (chunk.client and chunk.tag.name == 'reqend') or \
           (chunk.backend and (chunk.tag.name == 'backendclose' or
                               chunk.tag.name == 'backendreuse')):
            self.complete = True
            if chunk.tag.name == 'backendreuse':
                # backend reuse need a special case to get the next backend
                # request, to set it as active as soon as it is created
                # as no backendopen is there
                self.__class__._lines[self.fd] = True

            else:
                del self.__class__._lines[self.fd]

        self.chunks.append(chunk)
        return self.complete

    def __str__(self):
        res = "<%s %s" % (self.__class__.__name__, self.fd)
        for c in self.chunks:
            res += "\n\t%s" % (c)
        res += ">"
        return res
