=======
varnish
=======

varnish is a MIT-licensed library to access varnish-cache shared memory.
It uses ctypes to call function in the C library libvarnishapi, distributed as part of varnish.


  >>> import varnish
  >>> v = varnish.Varnish()
  >>> s = v.read_stats()
  >>> print s
  <VarnishStats[2012-03-01 17:50:02.101721] - 196 elements>