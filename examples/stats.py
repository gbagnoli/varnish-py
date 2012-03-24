#!/usr/bin/env python

""" Example script that shows how to access the stats of a varnish server
    This will connect to the default instance

    Example output (on a test instance):

$ python examples/stats.py
All:
[2012/03/24: 17:41:11] HIT: 834252, MISS: 45916, TOTAL: 1071713 - 216 stats read
[2012/03/24: 17:41:12] HIT: 834266, MISS: 45916, TOTAL: 1071738 - 216 stats read
[2012/03/24: 17:41:13] HIT: 834302, MISS: 45916, TOTAL: 1071788 - 216 stats read
Filtered:
[2012/03/24: 17:41:14] HIT: 834328, MISS: 45916, TOTAL: 1071825 - 3 stats read
[2012/03/24: 17:41:15] HIT: 834331, MISS: 45916, TOTAL: 1071830 - 3 stats read
[2012/03/24: 17:41:16] HIT: 834335, MISS: 45916, TOTAL: 1071835 - 3 stats read
"""

import time
import varnish

def print_totals(instance):

    # get current stats from the server
    stats = instance.stats.read()

    # stats is a dict-like instance. Stats can be accessed by attribute too
    print("[{0}] HIT: {1}, MISS: {2}, TOTAL: {3} - {4} stats read"\
            .format(stats.timestamp.strftime('%Y/%m/%d: %H:%M:%S'),
                    stats.cache_hit,
                    stats.cache_miss,
                    stats.client_req,
                    len(stats)))
    return stats


if __name__ == '__main__':

    try:
        # using the context manager to avoid explicit init()/close()
        with varnish.Instance() as v:

            print "All:"
            for i in xrange(3):
                print_totals(v)
                time.sleep(1)

            # we can filter out everything and add only needed stats
            v.stats.include('cache_hit')\
                   .include('cache_miss')\
                   .include('client_req')

            print("Filtered:")
            for i in xrange(3):
                print_totals(v)
                time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted")
