#!/usr/bin/env python
####################################################################################
# Copyright (c) 2009, Centre for Advanced Internet Architectures
# Swinburne University of Technology, Melbourne, Australia
# (CRICOS number 00111D).
#
####################################################################################
#
# check_path_hunting_intervals.py: A script to detect path hunting events in a 
# MRT dump file
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
import sys
d=BGPDump(sys.argv[1])
prefdict={}
prefints={}

for mrth, bgph,bgpm in d:
    len=0
    for a in bgpm.data.attributes:
        if a.type == 2:
            for s in a.data.segments:
                len=len+s.len
    if bgpm.data.announced:
        for r in bgpm.data.announced:
            rs=socket.inet_ntoa(r.prefix)+"/"+str(r.len)
            if rs in prefdict:
                if len > prefdict[rs][1] and prefdict[rs][1]:
                    if mrth.ts-prefdict[rs][0]<300:
                        if rs in prefints:
                            prefints[rs].append(mrth.ts-prefdict[rs][0])
                        else:
                            prefints[rs]=[mrth.ts-prefdict[rs][0]]
            prefdict[rs]=[mrth.ts,len]
    if bgpm.data.withdrawn:
        for r in bgpm.data.withdrawn:
            rs=socket.inet_ntoa(r.prefix)+"/"+str(r.len)
            if rs in prefdict:
                if len > prefdict[rs][1] and prefdict[rs][1]:
                    if mrth.ts-prefdict[rs][0]<300:
                        if rs in prefints:
                            prefints[rs].append(mrth.ts-prefdict[rs][0])
                        else:
                            prefints[rs]=[mrth.ts-prefdict[rs][0]]
            prefdict[rs]=[mrth.ts,0]


for k in sorted(prefints.keys()):
	print k,
	for ints in prefints[k]:
		print " " + str(ints),
	print " "

