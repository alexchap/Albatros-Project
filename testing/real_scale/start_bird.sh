#! /bin/sh

# This script start the official bird daemon on the nsl topology
# Topology overview : eval-topo.ppt
# Configuration files directory : conf-bird/
# NO DAMPING IS ACTIVATED WITH THIS TOPOLOGY

BIRD='/opt/acnds_11_2/bird/compiled/sbin/bird';
BIRDC="$BIRD"'c';

CONF_PREFIX='/opt/acnds_11_2/conf-bird/bird.10.0.0.';
CONF_SUFFIX='.conf';
DBG_PREFIX='/opt/acnds_11_2/log-dbg/bird-rt-';
DBG_SUFFIX='.debug';
SOCKET_PREFIX='/opt/acnds_11_2/sockets/bird-'"$RT_PREFIX";
SOCKET_SUFFIX='.c';


# Loop over all 27 nodes and start bird

for i in `seq 1 27`
do
  # start node i
  echo "Starting router $i"
  $BIRD -c "$CONF_PREFIX""$i""$CONF_SUFFIX" -s  "$SOCKET_PREFIX""$i""$SOCKET_SUFFIX" -D  "$DBG_PREFIX""$i""$DBG_SUFFIX" &

  # start stat_collector for node i

  # TODO

done


# Start log collector (i.e connect to birdc and execute some
# commands at regular time intervals)
# We keep track of the following :
# - memory status for each protocol (show memory)
# - statistics for each protocol (show protocols all)


# Start feeder (node with ip 10.0.0.3)
./start_feeder.sh &
