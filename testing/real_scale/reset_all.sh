#!/bin/sh

# This script kills all bird instances and delete all 
# log and debugging files
pkill bird
rm ./log-dbg/*.log
rm ./log-dbg/*.debug

echo "Daemons cleaned and log+debug files removed"
