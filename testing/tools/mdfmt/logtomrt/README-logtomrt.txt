Mattia Rossi                                                                                                                                 
Centre for Advanced Internet Architectures,                                                                                                  
Swinburne University of Technology,                                                                                                          
Melbourne, Australia                                                                                                                         
CRICOS number 00111D                                                                                                                         

30th July, 2009

----------------------------------------------
OVERVIEW                                      
----------------------------------------------

The LogToMRT tool converts Quagga text log files 
into compact binary MRT BGP4MP type dumps. 
This tool has been tested with Python 2.5 and Quagga 
text log dumps from Quagga 0.99.9 and higher.

This tool is part of the MDFMT 
and can be found in folder logtomrt.
The following files are part of the tool:

        README-logtomrt
        logtomrt-0.1.py

-----------------------
LICENCE                
-----------------------

This tool is released under a new BSD License. For more details
please refer to the included source files.

-----------------------
USAGE                  
-----------------------

Execute the script as follows:

        python logtomrt-0.1.py -l LOGFILE -m MRTFILE -a ASIPFILE -i LOCIP

LOGFILE   is the input text log file
MRTFILE   is the output MRT file
ASIPFILE  is a text file containing IPv4 address to AS number mappings
          of the participating routers.
          This is necessary to distinguish between different BGP sessions,
          and allows to insert information not possible to retrieve from
          the text log file.
LOCIP     is the IP address of the router that collected the data and created
          the text log file.

----------------------
ADDITIONAL INFORMATION
----------------------

LogToMRT works only with a patched dpkt library which allows the use
of 4 byte AS numbers. The patchset is part of the MDFMT project and 
should be located in folder dpkt-patchset.
The complete MDFMT can be obtained at:

        http://caia.swin.edu.au/urp/bgp/tools.html

Refer to the dpkt-patchset README for more information 
on how to install dpkt and the patchset.

For more details on the logtomrt tool, read the documentation at [2]

----------------------------------------------
KNOWN LIMITATIONS
----------------------------------------------

LogToMRT only extracts IPv4 update messages. It needs a text log file
which includes also the initial OPEN message between two peering BGP
speakers, which is needed to determine, whether to use 4 byte AS numbers 
or not. 

The LogToMRT tool has been tested only with text log files containing a single
peering session, but is also designed to work with multiple BGP sessions.

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
