#! /usr/bin/perl

use strict;
use warnings;

# Print protocol BGP for each neighbor
my @lines = `cat ASIP`;
my $dev = 'tap12';

foreach my $line (@lines) {
   my ($ip, $as) = split(/\s/,$line);

  # Add ip to interface
  `sudo ip addr add $ip/32 dev $dev`;
  # Add ip to routing table
  `sudo ip ro add $ip/32 dev $dev`;

}
