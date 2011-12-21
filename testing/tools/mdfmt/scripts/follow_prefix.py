#!/usr/bin/env python
####################################################################################
# Copyright (c) 2009, Centre for Advanced Internet Architectures
# Swinburne University of Technology, Melbourne, Australia
# (CRICOS number 00111D).
#
####################################################################################
#
# follow_prefix.py: A script to draw an update timeline for a prefix in a BGP network using
# multiple MRT dump files
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

import socket
import struct
from pybgpdump import BGPDump
import sys

a=[]
#List of dumpfiles start from the second argument
for i in range(2,len(sys.argv)):
	a.append(BGPDump(sys.argv[2]))

dict={}
count=0
for d in a:
    #The first dumpfile is number 1, the second number 2 and so on..
    count=count+1
    for mrth,bgph,bgpm in d:
        if bgpm.data.withdrawn:
            for el in bgpm.data.withdrawn:
                #Prefix is the first argument
                if el.prefix==socket.inet_aton(sys.argv[1]) and el.len==24:
                    for attr in bgpm.data.attributes:
                        if attr.type==2:
                            break
                    pathstr=""
                    for seg in attr.data.segments:
                        for asn in seg.data:
                            pathstr=pathstr+" "+str(asn)
                    for attr2 in bgpm.data.attributes:
                        if attr2.type==3:
                            break
                    nexthop=socket.inet_ntoa(struct.pack('>L',bgph.src_ip))
                    pfx=socket.inet_ntoa(el.prefix)+"/"+str(el.len)
                    if (mrth.ts in dict):
                        dict[mrth.ts].append(["w",count,nexthop,pfx,pathstr])
                    else:
                        dict[mrth.ts]=[["w",count,nexthop,pfx,pathstr]]
        if bgpm.data.announced:                 		
            for el in bgpm.data.announced:
                #Prefix is the first argument
                if el.prefix==socket.inet_aton(sys.argv[1]) and el.len==24:
                    for attr in bgpm.data.attributes:
                        if attr.type==2:
                            break
                    pathstr=""
                    for seg in attr.data.segments:
                        for asn in seg.data:
                            pathstr=pathstr+" "+str(asn)
                    for attr2 in bgpm.data.attributes:
                        if attr2.type==3:
                            break
                    nexthop=socket.inet_ntoa(struct.pack('>L',bgph.src_ip))
                    pfx=socket.inet_ntoa(el.prefix)+"/"+str(el.len)
                    if (mrth.ts in dict):
                        dict[mrth.ts].append(["a",count,nexthop,pfx,pathstr])
                    else:
                        dict[mrth.ts]=[["a",count,nexthop,pfx,pathstr]]

print "Results:"
for k in sorted(dict.keys()):
	for j in dict[k]:
		print time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(k)) + " " + str(k) + " " + j[0] + " " + str(j[1]) + " " + j[2] + " " + j[3] + " " + j[4]
