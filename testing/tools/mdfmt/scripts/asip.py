#!/usr/bin/env python
####################################################################################
# Copyright (c) 2009, Centre for Advanced Internet Architectures
# Swinburne University of Technology, Melbourne, Australia
# (CRICOS number 00111D).
#
####################################################################################
#
# asip.py: A script to extract AS number to IP address mappings from a
# MRT dump file. Also detects the use of 4 byte AS numbers. Generates
# A file suitable for use with the Update Regenerator.
# See README-scripts for details.
# 
####################################################################################
#
# This software was developed by Mattia Rossi <mrossi@swin.edu.au>
#
# This software has been made possible in part by a grant from
# the Cisco University Research Program Fund at
# Community Foundation Silicon Valley
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The names of the authors, the "Centre for Advanced Internet Architecture"
#    and "Swinburne University of Technology" may not be used to endorse
#    or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
###############################################################################

from pybgpdump import BGPDump
import socket
import struct
import sys

ipas={}
as4=0

d=BGPDump(sys.argv[1])
for mrth,bgph,bgpm in d:
    srcipdot=socket.inet_ntoa(struct.pack('>L',bgph.src_ip))
    if srcipdot not in ipas:
        ipas[srcipdot]=[bgph.src_as]
        for el in bgpm.data.attributes:
            if el.type==2:
                for seg in el.data.segments:
                    #find returns >0 if not found, so this is true for an AS4Path:
                    if repr(seg).find("ASPath"):
                        as4=1
                    else:
                        as4=0
        if as4==0:
            ipas[srcipdot].append(0)
        else:
            ipas[srcipdot].append(1)
for e in ipas.keys():
	print e + " " + str(ipas[e][0]) + " " + str(ipas[e][1])
