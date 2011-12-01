#!/bin/sh

# This script generates a flapping behavior for one route

# Parameters
INTERVAL=10;
FROUTE="211.11.11.11/32" # Fake route that flaps
TABLE="flap";

# GET the default gateway
DEFAULT_GW=`ip ro sh | grep 'default via .* dev' | awk '{ print $3; }'`

if [ ${#DEFAULT_GW} -lt 1 ]; then 
      echo "Error: You need a default gateway. Main routing table is shown here :";
      ip ro;
else
      echo "Flapping of route $FROUTE enabled every $INTERVAL seconds";
      while true;do
        sudo ip ro add "$FROUTE" via "$DEFAULT_GW" ta "$TABLE"
	echo "`date` : ADD route $FROUTE"
        sleep "$INTERVAL";
        sudo ip ro del "$FROUTE" via "$DEFAULT_GW" ta "$TABLE"
	echo "`date` : DEL route $FROUTE"
        sleep "$INTERVAL";
      done
fi
