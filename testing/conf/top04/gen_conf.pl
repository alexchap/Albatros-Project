#! /usr/bin/perl

use strict;
use warnings;

# Print basic  configuration options
print  "
# BIRD configuration file for router A

log \"/var/log/bird-top04-rta.log\" all;
debug protocols all;

router id 10.10.10.11;
listen bgp address 10.10.10.11 port 179;

# watch up/down state of interfaces
protocol device {
    debug all;
    scan time 10;
}

# Directly connected routes
protocol direct {
    interface \"tap11\";
    debug all;
}
";

# Print protocol BGP for each neighbor
my @lines = `cat ASIP`;

foreach my $line (@lines) {
   my ($ip, $as) = split(/\s/,$line);

   print 
   "
# BGP daemon
protocol bgp {
   description \"BGP daemon connected to as ".$as." and ip ".$ip."\";
   debug all;

   # Specific config for BGP 
   local as 65011;
   source address 10.10.10.11;
   multihop;
   next hop self;
   path metric 1;

   # Route damping configuration
   route damping;
   cut_threshold 2500;
   reuse_threshold 1000;
   tmax_hold 3000;
   half_time_reachable 900;
   half_time_unreachable 900;

   gateway recursive;

    # Timers
    hold time 240;
    startup hold time 240;
    connect retry time 120;
    keepalive time 80;
    start delay time 5;
    
    # Route
    export none;
    import filter {
       accept;
    };
   "
."neighbor ".$ip." as ".$as.";"
."\n}\n\n";
}
