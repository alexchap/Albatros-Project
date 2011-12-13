#!/bin/sh

# This script kills all bird instances and delete all 
# log and debugging files
pkill bird
rm *.log
rm *.debug
