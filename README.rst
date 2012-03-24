=======
varnish
=======

varnish is a MIT-licensed library to access varnish-cache shared memory.
It uses ctypes to call function in the C library libvarnishapi, distributed as part of varnish.


  >>> import varnish
  >>> with varnish.Instance() as v:
  ...     stats = v.stats.read()
  ...     print stats
  ...
  <VarnishStatsReading[2012-03-21 09:23:09.088649] - 196 elements>

See ``examples/stats.py`` for more about reading stats.
