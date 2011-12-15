#! /usr/bin/perl

use warnings;
use strict;
use Time::Local;
use Data::Dumper;

my @full_days
    = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
my @full_months
    = qw( January February March April May June July August September October November December );
my %months
    = qw( Jan 1 Feb 2  Mar 3 Apr 4 May 5 Jun 6 Jul 7 Aug 8 Sep 9 Oct 10 Nov 11 Dec 12 );

# This script processes the stats collected from the routers

my $STAT_PREFIX     = "stats-rt-";
my $STAT_SUFFIX     = ".stat";
my $STAT_DIR        = "./stats/";
my $OUT_DIR         = "./processed/";
my $OUT_FILE_PREFIX = $STAT_PREFIX;
my $OUT_FILE_SUFFIX = ".processed";

# process stats for each router
foreach my $j ( 1 .. 27 ) {
    process_stats_router($j);
}

# Function that create stats per router and saves them to disk
sub process_stats_router {

    my $router            = shift;
    my $file_stats_router = $STAT_DIR . $STAT_PREFIX . $router . $STAT_SUFFIX;
    my $i;    # used for discriminating bgp protocols during each timestamp
    my $nb_iterations = 0;

    # We will only care for the evolution of updates/withdrawals received from
    # all neighbors (sum !) and for the evolution of updates that have been
    # damped
    my @IU_received;
    my @IW_received;
    my @IU_damped;

    # temp totals for all combinations, filled for each timestamp
    my %totals;

    # import updates, import withdraws, export updates, export withdraws
    # The order is important !!
    my @row_types = ( 'IU', 'IW', 'EU', 'EW' );
    my @col_types = (
        'received', 'rejected', 'filtered', 'ignored',
        'accepted', 'damped'
    );

    open( my $CURRENT_STATS, '<', $file_stats_router )
        or die("Unable to open $file_stats_router");
    while ( my $line = <$CURRENT_STATS> ) {
        chomp $line;
        next if $line =~ /^#.*/;
        if ( $line =~ /^[a-zA-Z]/ ) {

            # Timestamp = beginning of new record
            my $timestamp = get_timestamp_date($line);
            $i = 0;

            # Save previous results
            if ( $nb_iterations > 0 ) {
                push( @IU_received, $totals{'IU'}{'received'} );
                push( @IW_received, $totals{'IW'}{'received'} );
                push( @IU_damped,   $totals{'IU'}{'damped'} );
            }

            # reset totals
            foreach my $row (@row_types) {
                foreach my $col (@col_types) {
                    $totals{$row}{$col} = 0;
                }
            }
            $nb_iterations++;
        }
        else {
            if ( $line =~ /^[0-9]+.*/ ) {

                # new entry
                my @entry
                    = ( $line
                        =~ m/^([0-9]+|-+)\t([0-9]+|-+)\t([0-9]+|-+)\t([0-9]+|-+)\t([0-9]+|-+)\t*([0-9]+|-+)*/
                    );

                # Do some cleaning : add 1 entry if no damping detected
                if ( not defined $entry[$#entry] ) {
                    $entry[$#entry] = 0;
                }

                # $i is the row index and $k the col index !
                foreach my $k ( 0 .. $#entry ) {
                    if ( $entry[$k] =~ /^---/ ) {
                        $entry[$k] = 0;
                    }
                    $totals{ $row_types[$i] }{ $col_types[$k] }
                        += int( $entry[$k] );
                }
                $i++;
            }
            else {

                # blank line -> next protocol
                $i = 0;
            }
        }
    }
    close($CURRENT_STATS);

    # Save data to disk
    mkdir($OUT_DIR);
    my $filerouter = $OUT_DIR . $OUT_FILE_PREFIX . $router . $OUT_FILE_SUFFIX;
    open( OUTFILE, "> $filerouter" );
    foreach my $elem (@IU_received) {
        print OUTFILE $elem . "\t";
    }
    print OUTFILE "\n";
    foreach my $elem (@IW_received) {
        print OUTFILE $elem . "\t";
    }
    print OUTFILE "\n";
    foreach my $elem (@IU_damped) {
        print OUTFILE $elem . "\t";
    }
    print "Stats for router $router saved to file $filerouter\n";
    close(OUTFILE);

}

# Function that get stats for all routers -> total over the whole network

# Convert Unix date to Timestamp
# The input should be of the form : "Tue Jun  7 17:48:44 2011"
sub get_timestamp_date {
    my $time_to_convert = shift;
    my ( $m, $d, $h, $min, $s, $y )
        = $time_to_convert
        =~ m/.*[a-zA-Z]+\s+([a-zA-Z]+)\s+([0-9]+)\s+([0-9]+):([0-9]+):([0-9]+)\s+CET\s+([0-9]+).*/;
    my $timestamp = timelocal( $s, $min, $h, $d, $months{$m} - 1, $y );

    return $timestamp;
}

# Convert Timestamp to Unix human readable date
sub get_full_date {
    my $time_to_convert = shift;
    my $long_date       = localtime($time_to_convert);
    chomp $long_date;

    return $long_date;
}

# Most useful function ever !
sub say {
    print @_, "\n";
}
