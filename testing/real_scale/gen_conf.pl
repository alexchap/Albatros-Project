#! /usr/bin/perl

use strict;
use warnings;


# Print protocol BGP for each neighbor
my @lines = `cat ASIP`;

foreach my $line (@lines) {
   my ($ip, $as) = split(/\s/,$line);

   print 
   "
# BGP daemon
protocol bgp {
  local as 65002;
  neighbor ".$ip." as ".$as.";
  source address 10.0.0.3;
  export none;
  import all;
\n}\n\n";
}
