#! /bin/sh

# This script start the official bird daemon on the nsl topology
# Topology overview : eval-topo.ppt
# Configuration files directory : conf-bird/
# NO DAMPING IS ACTIVATED WITH THIS TOPOLOGY

# TODO: change log files in each configuration file !

BIRD='/opt/acnds_11_2/bird/compiled/sbin/bird';
BIRDC="$BIRD"'c';

CONF_PREFIX='/opt/acnds_11_2/conf-bird/bird.10.0.0.';
CONF_SUFFIX='.conf';
DBG_PREFIX='/opt/acnds_11_2/log-dbg/bird-rt-';
DBG_SUFFIX='.debug';
SOCKET_PREFIX='/usr/local/var/run/'"$RT_PREFIX";
SOCKET_SUFFIX='.c';

# Loop over all 27 nodes and start bird

for i in 1..27
do

$BIRD -c "$CONF_PREFIX""$i""$CONF_SUFFIX" -s  "$SOCKET_PREFIX""$i""$SOCKET_SUFFIX" -D  "$DBG_PREFIX""$i""$DBG_SUFFIX" &

done


# Start feeder (node with ip 10.0.0.3)

# TODO

# Start log collector (i.e connect to birdc and execute some
# commands at regular time intervals)
# We keep track of the following :
# - memory status for each protocol (show memory)
# - statistics for each protocol (show protocols all)


# TODO
