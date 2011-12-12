#!/bin/sh

sudo birdc -s /usr/local/var/run/bird_rta.ctl <<FOO
sh dampened paths "bgp*"
quit
FOO > out
