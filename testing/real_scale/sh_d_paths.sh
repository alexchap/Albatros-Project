#!/bin/sh
i=10;
bird/compiled/sbin/birdc -s sockets/bird-"$i".ctl <<FOO
sh protocols all "bgp*"
quit
FOO > out | egrep -A 4 'Route change stats'
