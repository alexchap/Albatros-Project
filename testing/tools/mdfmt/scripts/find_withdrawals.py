#!/usr/bin/env python
####################################################################################
# Copyright (c) 2009, Centre for Advanced Internet Architectures
# Swinburne University of Technology, Melbourne, Australia
# (CRICOS number 00111D).
#
####################################################################################
#
# find_withdrawals.py: A script to extract withdrawals from an MRT dump file
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
import time

d=BGPDump(sys.argv[1])                                                                                             
for mrth,bgph,bgpm in d:                                                                                          
	if bgpm.data.withdrawn:                                                                                       
		for e in bgpm.data.withdrawn:                                                                         
			a=BGPDump(sys.argv[1])
			for mrt_h,bgp_h,bgp_m in a:                                                                   
				if mrt_h.ts>=mrth.ts:                                                                 
					break                                                                         
				if bgp_m.data.announced:                                                              
					for k in bgp_m.data.announced:                                                
						if e.prefix == k.prefix and e.len == k.len:                           
							print socket.inet_ntoa(e.prefix)+"/"+str(e.len) + " time: " + str(mrth.ts) + " " + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(mrth.ts)) + " nexthop: " + socket.inet_ntoa(struct.pack('>L',bgph.src_ip))
