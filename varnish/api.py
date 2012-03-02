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
import inspect
import logging
from ctypes import (Structure,
                    CFUNCTYPE,
                    POINTER,
                    c_void_p,
                    c_char_p,
                    c_int,
                    c_char,
                    c_uint,
                    c_uint64,
                    c_ulong,
                    py_object)
from .exc import (VarnishException,
                  VarnishUnHandledException)

varnishapi = ctypes.CDLL('libvarnishapi.so')
log = logging.getLogger(__name__)


# STRUCTURES
class _VSM_data(Structure):
    pass


class _VSC_C_main(Structure):
    pass


class _VSC_Point(Structure):
    __slots__ = ['cls', 'ident', 'name', 'fmt', 'flag', 'desc', 'ptr']
    _fields_ = [('cls', c_char_p),
                ('ident', c_char_p),
                ('name', c_char_p),
                ('fmt', c_char_p),
                ('flag', c_int),
                ('desc', c_char_p),
                ('ptr', c_void_p)]

# CTYPES DEFINITIONS
# generic
_VSM_New = varnishapi.VSM_New
_VSM_New.argtypes = []
_VSM_New.restype = POINTER(_VSM_data)

_VSM_diag_f = CFUNCTYPE(None, c_void_p)
_VSM_Diag = varnishapi.VSM_Diag
_VSM_Diag.argtypes = [POINTER(_VSM_data), _VSM_diag_f, py_object]
_VSM_Diag.restype = None

_VSM_n_Arg = varnishapi.VSM_n_Arg
_VSM_n_Arg.argtypes = [POINTER(_VSM_data), c_char_p]
_VSM_n_Arg.restype = c_int

_VSM_Close = varnishapi.VSM_Close
_VSM_Close.argtypes = [POINTER(_VSM_data)]
_VSM_Close.restype = None

_VSM_Delete = varnishapi.VSM_Close
_VSM_Delete.argtypes = [POINTER(_VSM_data)]
_VSM_Delete.restype = None

# stats
_VSC_Setup = varnishapi.VSC_Setup
_VSC_Setup.argtypes = [POINTER(_VSM_data)]
_VSC_Setup.restype = None

_VSC_Open = varnishapi.VSC_Open
_VSC_Open.argtypes = [POINTER(_VSM_data), c_int]
_VSC_Open.restype = c_int

_VSC_Arg = varnishapi.VSC_Arg
_VSC_Arg.argtypes = [POINTER(_VSM_data), c_int, c_char_p]
_VSC_Arg.restype = c_int

_VSC_Main = varnishapi.VSC_Main
_VSC_Main.argtypes = [POINTER(_VSM_data)]
_VSC_Main.restype = POINTER(_VSC_C_main)

_VSC_iter_f = CFUNCTYPE(c_int, c_void_p, POINTER(_VSC_Point))
_VSC_Iter = varnishapi.VSC_Iter
_VSC_Iter.argtypes = [POINTER(_VSM_data), _VSC_iter_f, py_object]
_VSC_Iter.restype = c_int

# logs
_VSL_S_CLIENT = (1 << 0)
_VSL_S_BACKEND = (1 << 1)
_VSL_tags_len = 256
_VSL_tags = (c_char_p * _VSL_tags_len).in_dll(varnishapi, 'VSL_tags')

try:
    _VSL_Name2Tag = varnishapi.VSL_Name2Tag
    _VSL_Name2Tag.argtypes = [c_char_p, c_int]
    _VSL_Name2Tag.restype = c_int

except AttributeError:
    _VSL_Name2Tag = None

_VSL_Setup = varnishapi.VSL_Setup
_VSL_Setup.argtypes = [POINTER(_VSM_data)]
_VSL_Setup.restype = None

_VSL_Open = varnishapi.VSL_Open
_VSL_Open.argtypes = [POINTER(_VSM_data), c_int]
_VSL_Open.restype = c_int

# TODO: define enum_vsl_tag!
                        # return priv,     tag,   fd,
                        # len,    spec,   ptr,      bitmap
_VSL_handler_f = CFUNCTYPE(c_int, c_void_p, c_int, c_uint,
                           c_uint, c_uint, c_char_p, c_uint64)
_VSL_Dispatch = varnishapi.VSL_Dispatch
_VSL_Dispatch.argtypes = [POINTER(_VSM_data), _VSL_handler_f, py_object]
_VSL_Dispatch.restype = c_int


__all__ = ['varnishapi', 'init', 'close', 'delete', 'set_diagnostic_function',
           'clear_diagnostic_function', 'access_instance', 'stats_open',
           'stats_setup', 'stats_main', 'stats_init', 'stats_iterate',
           'stats_filter', 'stats_exclude']


class VarnishStatsPoint(object):
    """ Python object used to copy the _VSC_Point structure """
    __slots__ = ['cls', 'ident', 'name', 'flag', 'desc',
                'value', 'full_name']

    def __init__(self, vsc_point):
        self.cls = str(vsc_point.cls)
        self.ident = str(vsc_point.ident)
        self.name = str(vsc_point.name)
        assert vsc_point.fmt == 'uint64_t'
        self.flag = chr(vsc_point.flag)
        self.desc = str(vsc_point.desc)
        self.value = long(ctypes.cast(vsc_point.ptr, POINTER(c_ulong))[0])
        self.full_name = ""
        if self.cls:
            self.full_name = self.full_name + "%s." % (self.cls)

        if self.ident:
            self.full_name = self.full_name + "%s." % (self.ident)

        self.full_name = self.full_name + self.name

    def __str__(self):
        return "<%s %s = %s>" % (self.__class__.__name__, self.full_name,
                                 self.value)

    def __repr__(self):
        return "<%s %s = %s [%s]>" % (self.__class__.__name__,
                                      self.full_name,
                                      self.value,
                                      self.desc)

    def __eq__(self, other):
        return self.full_name == other.full_name


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
                return self._tags_by_name[key].code

        else:
            return key

    def __getitem__(self, key):
        key = self._to_code(key)
        return LogTag(code=key, name=self._tags_by_code[key])

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


def init():
    """ Allocate and initialize the handle used in the C API.
        This is the first thing you have to do.
        You can have multiple active handles at the same time referencing the
        same or different shared memory files
    """
    handle = _VSM_New()
    if not handle:
        raise VarnishException('Cannot initialize varnish C API')

    log.debug("Initialized varnish C API (handle at %s)", handle)
    return handle


def close(varnish_handle):
    _VSM_Close(varnish_handle)


def delete(varnish_handle):
    _VSM_Delete(varnish_handle)


def set_diagnostic_function(varnish_handle, function, private_data):
    """ Set the diagnostic reporting function """

    def _function(priv, fmt, *args):
        if priv:
            priv = ctypes.cast(priv, py_object).value
        function(priv, fmt, *args)

    c_function = _VSM_diag_f(_function)
    if not private_data is None:
        private_data = py_object(private_data)

    _VSM_Diag(varnish_handle, c_function, py_object(private_data))


def clear_diagnostic_function(varnish_handle):
    """ Remove a previously set diagnostic reporting function """
    _VSM_Diag(varnish_handle, None, None)


def access_instance(varnish_handle, instance_name):
    """ Configure which varnish instance to access """
    if _VSM_n_Arg(varnish_handle, instance_name) != 1:
        raise VarnishException('Cannot access instance %s', instance_name)


def stats_setup(varnish_handle):
    """ Setup handle for use with stats functions """
    _VSC_Setup(varnish_handle)


def stats_open(varnish_handle, diagnostic=False):
    """ Open shared memory for stats processing """
    diag = 1 if diagnostic else 0
    if _VSC_Open(varnish_handle, diag) != 0:
        raise VarnishException('Error open shared memory for stats processing')


def stats_main(varnish_handle):
    """ Return the main  handle """
    stats_handle = _VSC_Main(varnish_handle)
    if stats_handle is None:
        raise VarnishException('Cannot get main stats structure')

    return stats_handle


def stats_init(varnish_handle, diagnostic=False):
    """ Shortcut function for stats processing setup """
    stats_setup(varnish_handle)
    stats_open(varnish_handle, diagnostic)
    return stats_main(varnish_handle)


def stats_iterate(varnish_handle, callback, private_data=None):
    """ Iterate over all statistics counters calling callback for each counters
        not filtered out by pre-set filters
    """
    def _callback(priv, point):
        value = VarnishStatsPoint(point[0]) if not point is None else None
        if priv:
            priv = ctypes.cast(priv, py_object).value

        args = len(inspect.getargspec(callback).args)
        try:
            res = 1
            if args == 0:
                callback()

            elif args == 1:
                callback(value)

            else:
                callback(value, priv)

        except StopIteration:
            res = 1

        except Exception as e:
            res = 1  # FIXME: errors seems masked!
            print e
            raise e

        else:
            res = 0

        finally:
            return res

    c_callback = _VSC_iter_f(_callback)

    if not private_data is None:
        private_data = py_object(private_data)

    _VSC_Iter(varnish_handle, c_callback, private_data)


def stats_filter(varnish_handle, name, exclude=False):
    if exclude:
        name = "^%s" % (name)

    result = _VSC_Arg(varnish_handle, ord('f'), name)
    if result == -1:
        raise VarnishException('Cannot set filter %s' % (name))

    if result == 0:
        raise VarnishUnHandledException('Filter "f" unhandled: %s' % (name))


def stats_exclude(varnish_handle, name):
    stats_filter(varnish_handle, name, exclude=True)


def logs_setup(varnish_handle):
    """ Setup handle for use with logs functions """
    _VSL_Setup(varnish_handle)


def logs_open(varnish_handle, diagnostic=False):
    """ Attempt to open and map the shared memory file. """
    diag = 1 if diagnostic else 0
    if _VSL_Open(varnish_handle, diag) != 0:
        raise VarnishException('Error open shared memory for logs processing')


def logs_init(varnish_handle, diagnostic=False):
    """ Shortcut function for logs processing setup """
    logs_setup(varnish_handle)
    logs_open(varnish_handle, diagnostic)


def logs_name_to_tag(name, match_length=-1):
    """ Converts a name to a log tag code.
        match_length == -1 means len(name)
        Returns -1 if no tag matches
                -2 if multiple matches are found
                >= 0 tag code
    """
    return _VSL_Name2Tag(name, match_length)

# TODO: add filters!


def logs_dispatch(varnish_handle, callback, private_data=None):
    def _callback(priv, tag, fd, len_, spec, ptr, bitmap):
        if priv:
            priv = ctypes.cast(priv, py_object).value

        lchunk = LogChunk(tag, fd, len_, spec, ptr, bitmap)
        try:
            args = len(inspect.getargspec(callback).args)
            res = 1
            if args == 1:
                res = callback(lchunk)

            else:
                res = callback(lchunk, priv)

        finally:
            if res is None:
                res = 0
            return  res

    c_callback = _VSL_handler_f(_callback)
    if not private_data is None:
        private_data = py_object(private_data)

    return _VSL_Dispatch(varnish_handle, c_callback, private_data)
