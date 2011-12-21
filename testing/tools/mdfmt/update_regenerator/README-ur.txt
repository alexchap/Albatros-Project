Mattia Rossi                                                                                                                                 
Centre for Advanced Internet Architectures,                                                                                                  
Swinburne University of Technology,                                                                                                          
Melbourne, Australia                                                                                                                         
CRICOS number 00111D                                                                                                                         

30th July, 2009

----------------------------------------------
OVERVIEW                                      
----------------------------------------------

The Update Regenerator (UR) replays a recorded 
MRT dump file into a live BGP session.
This tool has been tested with Python 2.5 and 2.6,
and Quagga version 0.99.10 and higher as BGP peer.

This tool is part of the MDFMT 
and can be found in folder update_regenerator.
The following files are part of the UR:

        README-ur
        update_regenerator.py

-----------------------
LICENCE                
-----------------------

This tool is released under a new BSD License. For more details
please refer to the included source files.

-----------------------
USAGE                  
-----------------------

Execute the script as follows:

        ./update_regenerator.py -m MRTFILE -d DestIP -a ASIPFILE

MRTFILE   is the input MRT file (must contain an initial RIB update sequence).
	  Can be generated using the MRT-slice tool located in the mrt_slice
	  folder.
ASIPFILE  is a text file containing IPv4 address to AS number mappings
          of the participating routers. This needs to include information about 
	  the use of 4 byte AS numbers.
	  An entry has the form:
	  <IP address> <AS number> <1|0>, where 1 means using 4 byte AS numbers
	  and 0 means using 2 byte AS numbers.
	  This file can be generated from the input MRT file using the asip.py
	  script located in the scripts folder.
DestIP    is the destination IP address of the router the UR wants to connect to.

----------------------
ADDITIONAL INFORMATION
----------------------

The UR works only with a patched dpkt library which allows the use
of 4 byte AS numbers. The patchset is part of the MDFMT project and 
should be located in folder dpkt-patchset.
The complete MDFMT can be obtained at:

        http://caia.swin.edu.au/urp/bgp/tools.html

Refer to the dpkt-patchset README for more information 
on how to install dpkt and the patchset.

For more details on the UR, read the documentation at [2].

----------------------------------------------
KNOWN LIMITATIONS
----------------------------------------------

The UR can connect to only one peer, but can "impersonate" multiple peers. It has been tested only
with Quagga version 0.99.10 and higher. The capabilities advertised are hardcoded. It does not
implement a finite state machine, nor a server part to process incoming packets. It is a pure
injection tool.
Please refer to the documentation for details on how to set up a working peering session with a remote
BGP speaker.

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


