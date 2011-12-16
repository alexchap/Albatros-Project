#! /usr/bin/perl

use strict;
use warnings;

# Get all configuration files and enable damping on all of them

my @conf_files = glob("bird.10.0.0.*.conf");
my $dir = 'new';
mkdir($dir);

foreach my $file (@conf_files) {

open(current_file,'<',$file);
open(out_file,"> $dir/$file");

while (my $line = <current_file>) {
   print out_file $line;
   if($line =~/.*protocol bgp {.*/) {
   print out_file "        route damping;\n";
   }
}

close current_file;
close out_file;

}

print "New config files saved in directory $dir";
