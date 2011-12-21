Mattia Rossi                                                                                                                                 
Centre for Advanced Internet Architectures,                                                                                                  
Swinburne University of Technology,                                                                                                          
Melbourne, Australia                                                                                                                         
CRICOS number 00111D                                                                                                                         

30th July, 2009

----------------------------------------------
OVERVIEW                                      
----------------------------------------------

A collection of Python scripts, based on dpkt
to use in conjunction with the Update Regenerator
or for evaluating MRT dumps.

This scripts are part of the MDFMT 
and can be found in folder scripts.
The following files are included:

        README-scripts
	asip.py
	check_path_hunting_intervals.py
	find_withdrawals.py
	follow_prefix.py

-----------------------
LICENCE                
-----------------------

This scripts are released under a new BSD License. For more details
please refer to the included source files.

-----------------------
USAGE                  
-----------------------

asip.py:

  ./asip.py dumpfile > asipfile

Extracts AS numbers and IP addresses from a dump file
and adds information about 4 byte AS numbers.
Results are printed and can be redirected to a file.
The file works in conjunction with the Update Regenerator.


check_path_hunting_intervals.py:

  ./check_path_hunting_intervals.py dumpfile > textfile

Extracts information about path hunting events from a dump file.
Prints the results, which can be directed into a text file.


find_withdrawals.py:

  ./find_withdrawals.py dumpfile > textfile

Extracts withdrawn prefixes from a dump file, making sure
these prefixes have been previously announced.


follow_prefix.py:

  ./follow_prefix.py prefix dumpfile1 dumpfile2 dumpfile3 ... > textfile

Extracts a prefix from a set of dumpfiles, ordering the records 
chronologically. Allows to evaluate how a prefix propagates
through a network of BGP speakers.

----------------------
ADDITIONAL INFORMATION
----------------------

All scripts are based on pybgpdump and dpkt. They work best with a 
patched dpkt library which allows the use of 4 byte AS numbers. 
The patchset is part of the MDFMT project and is located 
in the folder dpkt-patchset.
The complete MDFMT can be obtained at:

        http://caia.swin.edu.au/urp/bgp/tools.html

Refer to the dpkt-patchset README for more information 
on how to install dpkt and the patchset.

For more details on the MDFMT scripts, read the documentation at [2].

----------------------------------------------
KNOWN LIMITATIONS
----------------------------------------------

These scripts have been developed for a specific project, although
they should be ready for generic use and should work out of the box.
They are not optimized and might be really slow.
Depending on the MRT dump file they might also not work at all.
They have only been tested with MRT dump files produced by Quagga 
version 0.99.10 and higher.

----------------------------------------------
RELATED READING
----------------------------------------------

[1] MRT dump formats draft:

        http://tools.ietf.org/html/draft-ietf-grow-mrt-08

[2] MRT dump file manipulation toolkit (MDFMT) - version 0.2
    (CAIA technical report) PDF format

        http://caia.swin.edu.au/reports/090730B/CAIA-TR-090730B.pdf

----------------------------------------------
ACKNOWLEDGEMENTS
----------------------------------------------

This project has been made possible in part by
a grant from the Cisco University Research Program
Fund at Community Foundation Silicon Valley
