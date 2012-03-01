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

import ctypes
import inspect
import logging
from ctypes import (Structure,
                    CFUNCTYPE,
                    POINTER,
                    c_void_p,
                    c_char_p,
                    c_int,
                    c_ulong,
                    py_object)
from .exc import (VarnishException,
                  VarnishUnHandledException)

varnishapi = ctypes.CDLL('libvarnishapi.so')
log = logging.getLogger(__name__)


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


__all__ = ['varnishapi', 'init', 'close', 'delete', 'set_diagnostic_function',
           'clear_diagnostic_function', 'access_instance', 'stats_open',
           'stats_setup', 'stats_main', 'stats_init', 'stats_iterate',
           'stats_filter', 'stats_exclude']


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
    stats_open(varnish_handle)
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
