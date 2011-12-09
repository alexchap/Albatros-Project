#!/bin/sh

# This script generates a flapping behavior for one route

# Parameters
INTERVAL=15;
FROUTE="211.11.11.12/32" # Fake route that flaps
TABLE="flap";
METRIC_HIGH=1000;
METRIC_LOW=100;
FLAP_TYPE=2; # 1 = add/remove route continuously -> generates updates and withdrawals
	     # 2 = add route with high metric first and the add/del route with lower metric 
	     #     -> only generates updates

# GET the default gateway
DEFAULT_GW=`ip ro sh | grep 'default via .* dev' | awk '{ print $3; }'`

if [ ${#DEFAULT_GW} -lt 1 ]; then 
      echo "Error: You need a default gateway. Main routing table is shown here :";
      ip ro;
else
      echo "Flapping of route $FROUTE enabled every $INTERVAL seconds";
      if [ $FLAP_TYPE -eq 2 ]; then
	echo "Added route with high metric first"
	sudo ip ro add "$FROUTE" via "$DEFAULT_GW" ta "$TABLE" metric "$METRIC_HIGH"
      fi
      while true;do
        sudo ip ro add "$FROUTE" via "$DEFAULT_GW" ta "$TABLE" metric "$METRIC_LOW"
	echo "`date` : ADD route $FROUTE"
        sleep "$INTERVAL";
        sudo ip ro del "$FROUTE" via "$DEFAULT_GW" ta "$TABLE" metric "$METRIC_LOW"
	echo "`date` : DEL route $FROUTE"
        sleep "$INTERVAL";
      done
fi
