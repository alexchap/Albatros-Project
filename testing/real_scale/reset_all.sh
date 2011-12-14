#!/bin/sh

# This script kills all bird instances and delete all 
# log and debugging files
echo "Kill daemons"
pkill bird
pkill python
pkill -9 start_feeder.sh 

echo "Killing collectors"
pkill start_collector

echo "Saving current stats to compressed archive last_stats.tar.gz"
tar -zcf last_stats.tar.gz stats

echo "Cleaning stats files"
rm ./stats/*.stat

echo "Saving current logs to compressed archive last_logs.tar.gz"
tar -zcf last_logs.tar.gz log-dbg

echo "Deleting logs"
rm ./log-dbg/*.log
rm ./log-dbg/*.debug

echo "Daemons cleaned and log+debug files removed"
