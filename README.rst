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

  >>> import varnish
  >>> def request_callback(request):
  ...     print repr(request)
  ...
  >>> with varnish.Instance() as v:
  ...     v.logs.dispatch_requests(request_callback)
  ...
  <ClientRequestLog XID: 987853649
    Client: 127.0.0.1:60411

    Timing:
        started   : 2012-05-22 14:07:23.253677
        completed : 2012-05-22 14:07:23.417131
        delay     : 6.3896e-05 [s]
        processing: 0.163139582 [s]
        deliver   : 0.000314236 [s]

    Request: HTTP/1.1 GET /
        headers   : MultiDict([('user-agent', 'curl/7.22.0 (x86_64-pc-linux-gnu) libcurl/7.22.0 OpenSSL/1.0.1 zlib/1.2.3.4 libidn/1.23 librtmp/2.3'), ('accept', '*/*'), ('host', 'www.example.com')])

    Hash: ['/', 'www.example.com']
    VCL Calls: MultiDict([('recv', 'lookup'), ('hash', 'hash'), ('miss', 'fetch'), ('fetch', 'deliver'), ('deliver', 'deliver')])

    Response: HTTP/1.1 200 OK [0B]
        headers   : MultiDict([('server', 'Apache/2.2.14 (Ubuntu)'), ('x-powered-by', 'PHP/5.3.2-1ubuntu4.15'), ('cache-control', 'max-age=60, public'), ('vary', 'Accept-Encoding'), ('content-type', 'text/html'), ('transfer-encoding', 'chunked'), ('date', 'Tue, 22 May 2012 12:07:23 GMT'), ('x-varnish', '987853649'), ('age', '0'), ('via', '1.1 varnish'), ('connection', 'keep-alive')])

