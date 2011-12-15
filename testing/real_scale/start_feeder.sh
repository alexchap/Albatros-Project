#!/bin/sh

# The feeder is router 10.0.0.3. It will receive updates from the 
# generator (special configuration file with the neighbors listed
# in file ASIP) and disseminate them throughout the topology

export BGP_PORT=38179
/opt/acnds_11_2/mdfmt/update_regenerator/update_regenerator.py -m /opt/acnds_11_2/updates/updates.20100401.1729 -d 10.0.0.3 -a /opt/acnds_11_2/mdfmt/test/ASIP
