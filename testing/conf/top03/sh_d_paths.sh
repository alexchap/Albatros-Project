#!/bin/sh

sudo birdc -s /usr/local/var/run/bird_rta.ctl <<FOO
sh bgp dampened paths
quit
FOO > out
