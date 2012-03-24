#!/usr/bin/env python

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

            for i in xrange(3):
                print_totals(v)
                time.sleep(1)

            # we can filter out everything and add only needed stats
            v.stats.include('cache_hit')\
                   .include('cache_miss')\
                   .include('client_req')
        
            for i in xrange(3):
                print_totals(v)
                time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted")
