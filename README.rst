=======
varnish
=======

varnish is a MIT-licensed library to access varnish-cache shared memory.
It uses ctypes to call function in the C library libvarnishapi, distributed as part of varnish.

Install
-------

On *ubuntu* and *debian*, you need to install ``libvarnishapi-dev`` package.

  $ sudo apt-get install libvarnishapi-dev

On *fedora*, you need to install ``varnish-libs-devel`` package

  $ sudo yum install varnish-libs-devel

Then, to install from github cloned sources:

  $ pip install -e ./
 
Currently there are **no** packages on pypi as **this is a work in progress** (many things are missing, some other do not work properly / do not work at all)


Example usage
-------------
 
Stats
-----

  >>> import varnish
  >>> with varnish.Instance() as v:
  ...     stats = v.stats.read()
  ...     print stats
  ...
  <VarnishStatsReading[2012-03-21 09:23:09.088649] - 196 elements>

See ``examples/stats.py`` for more about reading stats.

Logs
----

TODO
