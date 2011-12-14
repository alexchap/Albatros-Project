#! /bin/sh

# This script start the official bird daemon on the nsl topology
# Topology overview : eval-topo.ppt
# When any parameter is given to this script, then the
# router 10.0.0.3 will have route damping enabled (with default params)

THEBIRD='/opt/acnds_11_2/bird/compiled/sbin/bird'
OURBIRD='/opt/acnds_11_2/ourbird/compiled/sbin/bird'
CONF_PREFIX='/opt/acnds_11_2/conf-bird/bird.10.0.0.'
DEFAULT_CONF_SUFFIX='.conf'
DAMP_SUFFIX='-with-damping.conf'

DBG_PREFIX='/opt/acnds_11_2/log-dbg/bird-rt-'
DBG_SUFFIX='.debug'
SOCKET_PREFIX='/opt/acnds_11_2/sockets/bird-'"$RT_PREFIX"
SOCKET_SUFFIX='.ctl'

# Loop over all 27 nodes and start bird

for i in `seq 1 27`
do
  # Check damping activation
  if [ $# -gt 0 -a $i -eq 3 ]; then
	CONF_SUFFIX="$DAMP_SUFFIX"
	BIRD="$OURBIRD"
	DAMP=1
  else
	CONF_SUFFIX="$DEFAULT_CONF_SUFFIX"
	BIRD="$THEBIRD"
	DAMP=0
  fi

  # start node i
  echo "Starting router $i"
  SOCKET="$SOCKET_PREFIX""$i""$SOCKET_SUFFIX"
  $BIRD -c "$CONF_PREFIX""$i""$CONF_SUFFIX" -s "$SOCKET" -D  "$DBG_PREFIX""$i""$DBG_SUFFIX" &

  # start stat_collector for node i
  echo "Starting collector $i"
  ./start_collector.sh "$i" "$DAMP" "$SOCKET" &

done

# Start feeder (node with ip 10.0.0.3)
echo "Feeder will start in 10 seconds"
sleep 10
./start_feeder.sh &
