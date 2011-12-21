Mattia Rossi
Centre for Advanced Internet Architectures,
Swinburne University of Technology,
Melbourne, Australia
CRICOS number 00111D

30th July, 2009

----------------------------------------------
OVERVIEW
----------------------------------------------

The MRT slice tool takes a large MRT BGP4MP type dump containing
BGP update sequences, and cuts out slices for certain time intervals, 
which do not only contain the update messages of this time interval,
but also the updates of an initial RIB propagation.
This MRT slices can be used to reproduce a complete BGP session
between two BGP speakers as it would have been happened at the
exact time the updates were collected.

This tool is part of the MDFMT and can be found in folder mrt_slice.
The following files are part of the tool:

        README-mrtslice
        mrt_slice-0.1.py

-----------------------
LICENCE
-----------------------

This tool is released under a new BSD License. For more details
please refer to the included source files.

-----------------------
USAGE
-----------------------

Execute the script as follows:

	python mrt_slice-0.1.py -i INFILE -o OUTFILE -r RIBDUMP -t TIMESPAN

INFILE is the input MRT file - mandatory
OUTFILE is the output MRT file - mandatory
RIBDUMP is the MRT RIB dump file. This is optional. If it is given, 
	the start time will be determined by it, if it is not given, 
	the slice starts from the beginning of the MRT file, which should
	contain the initial RIB update messages.
TIMESPAN is the time interval of the slice. It can be indicated in seconds,
	minutes (by appending 'm'), hours (h), days (d) or weeks (w)

The resulting file will be an MRT BGP4MP type dump.

----------------------
ADDITIONAL INFORMATION
----------------------

The mrt_slice tool works only with a patched dpkt library 
which allows the use of 4 byte AS numbers. 
The patchset is part of the MDFMT project and
should be located in folder dpkt-patchset.
The complete MDFMT can be obtained at:

        http://caia.swin.edu.au/urp/bgp/tools.html

Refer to the dpkt-patchset README for more information
on how to install dpkt and the patchset.

For more details on the mrt_slice tool, read the documentation at [2].

----------------------------------------------
KNOWN LIMITATIONS
----------------------------------------------

If no MRT RIB dump (TableDumpV2) is given, the tool cuts a slice of
TIMESPAN form the beginning of the original MRT file.
This method assumes the original MRT file includes a RIB propagation
at the beginning of the update sequence.

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

