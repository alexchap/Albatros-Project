#!/bin/sh

# This script starts a collector for the router which ID is 
# given as argument. There are three parameters to give when
# calling the collector :
# 1) the router number
# 2) A boolean. 1 if damping enabled, 0 otherwise
# 3) The socket for this router
# The stats are stored in the STATS directory
# TODO: maybe later we would be interested in show dampened paths for the router 3 !

STATS_DIR='stats/'
STATS_PREFIX='stats-rt-'
STATS_SUFFIX='.stat'

THEBIRDC='/opt/acnds_11_2/bird/compiled/sbin/birdc'
OURBIRDC='/opt/acnds_11_2/ourbird/compiled/sbin/birdc'

# This defines the time interval between two collector tasks
INTERVAL=10

# Get router ID and damping params
i=$1
DAMP=$2
SOCKET=$3

STATS_FILE="$STATS_DIR""$STATS_PREFIX""$i""$STATS_SUFFIX"

echo "
# This is the output of show protocols all \"bgp*\"
# List of columns (7 or 8 if damping enabled) :
# received rejected filtered ignored accepted damped
# List of rows (MOD 4 !)
# - Import updates
# - Import withdraws
# - Export updates
# - Export withdraws
# Every $INTERVAL seconds, those stats are saved for each
# BGP proto. Protocols appear in alphabetical order !
" >>  "$STATS_FILE"

while true;do
   # date
   date >> "$STATS_FILE"
   # content
   if [ $DAMP -eq 1 -a $i -eq 3 ];then
      "$OURBIRDC" -s "$SOCKET" -v 'show protocols all "bgp*"' | egrep -A 4 'Route change stats' | egrep -A 4 'Route change stats' | grep -v 'Route' | awk '{print $3 "\t" $4 "\t" $5 "\t" $6 "\t" $7 "\t" $8 }' >> "$STATS_FILE"
   else
      "$THEBIRDC" -s "$SOCKET" -v 'show protocols all "bgp*"' | egrep -A 4 'Route change stats' | egrep -A 4 'Route change stats' | grep -v 'Route' | awk '{print $3 "\t" $4 "\t" $5 "\t" $6 "\t" $7 "\t" $8 }' >> "$STATS_FILE"
   fi

   sleep "$INTERVAL"

done

# TODO (not related to here but reminder : check # damped = # shown !
