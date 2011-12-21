Mattia Rossi
Centre for Advanced Internet Architectures,
Swinburne University of Technology,
Melbourne, Australia
CRICOS number 00111D

30th July, 2009


----------------------------------------------
OVERVIEW
----------------------------------------------

This README is part of the mdfmt-0.2.tar.bz2 tarball.
The following files are part of the dpkt patchset
and are located in the dpkt-patchset folder:
        README-dpkt-patchset
	dpkt-patchset.patch

Dpkt is a fast, simple packet creation / parsing library 
for Python, with definitions for the basic TCP/IP protocols
including BGP and the MRT routing information export format.

This patchset allows dpkt to process BGP 4 byte AS numbers
and MRT TableDumpV2 RIB dumps. It also includes additional
capabilities like Multiprotocol.

PyBGPdump is a Python library to extract MRT dump information.
It is a companion library to dpkt, and can be installed
without patching.

-----------------------
LICENCE
-----------------------

This patches are released under the new BSD License. For more details
please refer to the included source files.

-----------------------
USAGE
-----------------------

dpkt and patches:

- Get the latest dpkt version from svn (r54):

	svn checkout http://dpkt.googlecode.com/svn/trunk/ dpkt-read-only

- Copy the patchset to the dpkt folder:

	cp dpkt-patchset.patch dpkt-read-only/

- Patch dpkt:

	cd dpkt-read-only
	patch -p1 < dpkt-patchset.patch

- Install dpkt (as root):

	./setup.py install

pybgpdump:

- Get the latest version from svn:

        svn checkout http://pybgpdump.googlecode.com/svn/trunk/ pybgpdump-read-only

- Install (as root):

        ./setup.py install

-----------------------
CONFIGURATION
-----------------------

The patched dpkt can be used in any python script/program by
importing it with:

	import dpkt

The pybgpdump library can be used by importing the BGPDump command
as shown:

        from pybgpdump import BGPDump

and using it in a loop like the following:

        d=BGPDump(<yourfile>)
        for mrth,bgph,bgpm in d:
                ...

Variable mrth contains the MRT header, bgph the BGP header,
and bgpm the BGP message.

You may want to have a look at the MDFMT toolkit 
for an example usage.

	http://caia.swin.edu.au/urp/tools.html

the documentation of the MDFMT can be found at [2].

----------------------------------------------
KNOWN LIMITATIONS
----------------------------------------------

This patchset has been tested with Python versions 2.5 and 2.6, 
although it may work also on older versions.
If you experience any problems with any older Python version,
we suggest you to upgrade to version 2.5 or higher.

With revision 52 dpkt has been adapted for Python 2.6 and
newer, by renaming the 'as' variable to 'asn', as it is a 
reserved keyword.
This patches are designed to apply cleanly on revison 54.
It is not suggested to use any earlier revision or the dpkt
release version.

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

