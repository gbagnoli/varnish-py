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
import ctypes
from .vsm import _VSM_data
from ..exc import VarnishException


__all__ = ['setup', 'init', 'open_', 'name_to_tag', 'dispatch', 'LogTags']
varnishapi = ctypes.CDLL('libvarnishapi.so')


LogTag = collections.namedtuple('LogTag', ['code', 'name'])


class LogTags(collections.Mapping):

    def __new__(cls):
        if '_inst' not in vars(cls):
            cls._inst = super(LogTags, cls).__new__(cls)
            cls._inst._tags_by_code = dict()
            cls._inst._tags_by_name = dict()
            for code in xrange(_VSL_tags_len):
                name = _VSL_tags[code]
                if not name is None:
                    name = name.lower()
                    tag = LogTag(code=code, name=name)
                    cls._inst._tags_by_code[code] = tag
                    cls._inst._tags_by_name[name] = tag

        return cls._inst

    def _to_code(self, key):
        if isinstance(key, basestring):
            if _VSL_Name2Tag:
                res = _VSL_Name2Tag(key, -1)
                if res == -1:
                    return KeyError('No tag %s' % key)

                if res == -2:
                    raise KeyError("Multiple code for %s" % key)

                return res
            else:
                key = key.lower()
                return self._tags_by_name[key].code

        else:
            return key

    def __getitem__(self, key):
        key = self._to_code(key)
        return self._tags_by_code[key]

    def __iter__(self):
        return iter(self._tags_by_name)

    def __contains__(self, key):
        key = self._to_code(key)
        return key in self._tags_by_code

    def __len__(self):
        return len(self._tags_by_code)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr(self._tags_by_name)


class LogChunk(object):
    """ Python object that represent a log entry """

    def __init__(self, tag, fd, len_, spec, ptr, bitmap):
        self.tag = LogTags()[tag]
        self.fd = int(fd)  # file descriptor associated with this record
        self.client = spec == _VSL_S_CLIENT
        self.backend = spec == _VSL_S_BACKEND
        self.data = str(ptr)
        assert len(self.data) == len_
        self.bitmap = int(bitmap)

    def __str__(self):
        type_ = "client" if self.client else "backend"
        return "<LogChunk [%s] tag: %s data: %s>" % (type_, self.tag,
                                                     self.data)

    def __repr__(self):
        return str(self)


# logs
_VSL_S_CLIENT = (1 << 0)
_VSL_S_BACKEND = (1 << 1)
_VSL_tags_len = 256
_VSL_tags = (ctypes.c_char_p * _VSL_tags_len).in_dll(varnishapi, 'VSL_tags')

try:
    _VSL_Name2Tag = varnishapi.VSL_Name2Tag
    _VSL_Name2Tag.argtypes = [ctypes.c_char_p, ctypes.c_int]
    _VSL_Name2Tag.restype = ctypes.c_int

except AttributeError:
    _VSL_Name2Tag = None

_VSL_Setup = varnishapi.VSL_Setup
_VSL_Setup.argtypes = [ctypes.POINTER(_VSM_data)]
_VSL_Setup.restype = None

_VSL_Open = varnishapi.VSL_Open
_VSL_Open.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int]
_VSL_Open.restype = ctypes.c_int

# TODO: define enum_vsl_tag!
                        # return priv,     tag,   fd,
                        # len,    spec,   ptr,      bitmap
_VSL_handler_f = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p,
                                  ctypes.c_int, ctypes.c_uint,
                                  ctypes.c_uint, ctypes.c_uint,
                                  ctypes.c_char_p, ctypes.c_uint64)
_VSL_Dispatch = varnishapi.VSL_Dispatch
_VSL_Dispatch.argtypes = [ctypes.POINTER(_VSM_data),
                          _VSL_handler_f, ctypes.py_object]
_VSL_Dispatch.restype = ctypes.c_int


def setup(varnish_handle):
    """ Setup handle for use with logs functions """
    _VSL_Setup(varnish_handle)


def open_(varnish_handle, diagnostic=False):
    """ Attempt to open and map the shared memory file. """
    diag = 1 if diagnostic else 0
    if _VSL_Open(varnish_handle, diag) != 0:
        raise VarnishException('Error open shared memory for logs processing')


def init(varnish_handle, diagnostic=False):
    """ Shortcut function for logs processing setup """
    setup(varnish_handle)
    open_(varnish_handle, diagnostic)


def name_to_tag(name, match_length=-1):
    """ Converts a name to a log tag code.
        match_length == -1 means len(name)
        Returns -1 if no tag matches
                -2 if multiple matches are found
                >= 0 tag code
    """
    return _VSL_Name2Tag(name, match_length)


# TODO: add filters!
def dispatch(varnish_handle, callback, private_data=None):
    def _callback(priv, tag, fd, len_, spec, ptr, bitmap):
        if priv:
            priv = ctypes.cast(priv, ctypes.py_object).value

        lchunk = LogChunk(tag, fd, len_, spec, ptr, bitmap)
        try:
            res = callback(lchunk, priv)

        finally:
            if res is None:
                res = 0
            return  res

    c_callback = _VSL_handler_f(_callback)
    if not private_data is None:
        private_data = ctypes.py_object(private_data)

    return _VSL_Dispatch(varnish_handle, c_callback, private_data)
