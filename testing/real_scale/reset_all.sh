#!/bin/sh

# This script kills all bird instances and delete all 
# log and debugging files
echo "Kill daemons"
pkill bird
pkill python
pkill -9 start_feeder.sh 
echo "Del logs"
rm ./log-dbg/*.log
rm ./log-dbg/*.debug

echo "Daemons cleaned and log+debug files removed"
