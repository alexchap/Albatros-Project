#!/usr/bin/env python
####################################################################################
# Copyright (c) 2009, Centre for Advanced Internet Architectures
# Swinburne University of Technology, Melbourne, Australia
# (CRICOS number 00111D).
#
####################################################################################
#
# Update Regenerator: a tool for replaying recorded BGP updates
# in MRT format into live BGP sessions.
# Requires a 4 byte AS number capable dpkt version.
# See README-ur for details.
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

import dpkt
from pybgpdump import BGPDump
import socket
import struct
from optparse import OptionParser
import re
import time
import math
import os
import sys
import signal
import route_btoa

BGP_PORT = int(os.getenv("BGP_PORT", 179))
#MAX_UP_COUNT = 9000 * 11
MAX_UP_COUNT = 0
can_exit = False

def go_down(unused1,unused2):
    print "Going down"
    can_exit = True
    
def mkOpenPkt(asn,srcip, astype):
    bgppkt=dpkt.bgp.BGP()
    openpkt=bgppkt.Open(v=4, identifier=struct.unpack('!L',socket.inet_aton(srcip))[0],holdtime=180)
    if astype:
        if (asn>65535 ):
            openpkt.asn=23456
        else:
            openpkt.asn=asn
    else:
        openpkt.asn=asn
    openpkt.parameters=[]
    param1=openpkt.Parameter()
    cap1=param1.Capability(code=dpkt.bgp.CAP_MULTIPROTOCOL)
    multi=cap1.MultiProtocol(afi=1, res=0, safi=1)
    cap1.data=multi
    cap1.len=len(multi)
    param1.data=cap1
    param1.type=dpkt.bgp.CAPABILITY
    param1.len=len(cap1)
    openpkt.parameters.append(param1)
    if astype:
        param2=openpkt.Parameter()
        cap2=param2.Capability(code=dpkt.bgp.CAP_SUPPORT_AS4)
        cap2.data=struct.pack("!L", asn)
        cap2.len=len(cap2.data)
        param2.data=cap2
        param2.type=dpkt.bgp.CAPABILITY
        param2.len=len(cap2)
        openpkt.parameters.append(param2)
    param3=openpkt.Parameter()
    cap3=param3.Capability(code=dpkt.bgp.CAP_ROUTE_REFRESH_OLD) # Route Refresh old
    cap3.len=0
    param3.data=cap3
    param3.type=dpkt.bgp.CAPABILITY
    param3.len=len(cap3)
    openpkt.parameters.append(param3)
    param4=openpkt.Parameter()
    cap4=param4.Capability(code=dpkt.bgp.CAP_ROUTE_REFRESH) # Route Refresh old
    cap4.len=0
    param4.data=cap4
    param4.type=dpkt.bgp.CAPABILITY
    param4.len=len(cap4)
    openpkt.parameters.append(param4)
    openpkt.param_len=len(openpkt.parameters)
    #capabilities: AS4, MULTIPROTO for 1/1 and route refresh (old/new)
    bgppkt.data=openpkt.pack()
    bgppkt.len=len(bgppkt)
    return bgppkt.pack()   

def main():
    parser = OptionParser()
    parser.add_option("-m", "--mrtfile", dest="mrtfile", default="", 
                    help="mrt input file")
    parser.add_option("-d", "--dst",
                    dest="dstip", help="destination ip address")
    parser.add_option("-a", "--asip",
                    dest="asip", help="file containing ip address to as number mapping")
    
    (options, args) = parser.parse_args()
      
    if(not options.mrtfile or not options.dstip or not options.asip):
        parser.print_help()
        exit(-1)
      
    dstip=options.dstip
      
    ft=open(options.mrtfile, "r")
    starttime=struct.unpack("!I", ft.read(4))[0]

    print "Start time: " + str(starttime) + " - " + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(starttime))
    ft.close()
        
    srciplist={}

    keepalivetimer=30
    keepalive=dpkt.bgp.BGP(type=dpkt.bgp.KEEPALIVE)
    keepalive.len=len(keepalive)

    #start connecting to quagga
    f=open(options.asip, "r")
    for line in f:
        m=re.search("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ([0-9]+) ([01]).*", line)
        if (m):
            srciplist[m.group(1)]=[int(m.group(2)),int(m.group(3))]
            print "connecting to: " + dstip +" from " + m.group(1) + " asn: " + str(srciplist[m.group(1)][0]) + "\n"
            srciplist[m.group(1)].append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            con=1
            while(con != 0): #try to connect to quagga until it works
                srciplist[m.group(1)][2].close()
                srciplist[m.group(1)][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srciplist[m.group(1)][2].bind((m.group(1), BGP_PORT))
                con=srciplist[m.group(1)][2].connect_ex((dstip, BGP_PORT))
            print "connected!\n"
            srciplist[m.group(1)][2].send(mkOpenPkt(srciplist[m.group(1)][0],m.group(1),srciplist[m.group(1)][1]))
            time.sleep(1)
            srciplist[m.group(1)][2].send(keepalive.pack())

    dump = BGPDump(options.mrtfile)
    found=0

    reltime=starttime
    prevtime=time.time()
    print "Sending updates..."
    out = sys.stdout.write
    up_count = 0
    for mrt_h, bgp_h, bgp_m in dump:
        up_count += 1
        if up_count == MAX_UP_COUNT:
            break
        #route_btoa.out_msg(out, mrt_h, bgp_h, bgp_m)
        srcipdot = socket.inet_ntoa(struct.pack('>L',bgp_h.src_ip))
        #Some magic if the time in the MRT dump advances by a second
        while (reltime < mrt_h.ts):
            current=time.time()
            next=math.floor(current)+1
            #Sleep until the current second is finished before processing the next updates
            time.sleep(next-current)
            keepalivetimer=keepalivetimer-1
            if(keepalivetimer==0):
                for e in srciplist.keys():
                    srciplist[e][2].send(keepalive.pack())
                keepalivetimer=30
            reltime = reltime + 1
        #Send all updates recorded within the same second timeframe
        if srcipdot in srciplist.keys():
            srciplist[srcipdot][2].send(bgp_h.data)

    print "Updates finished. Press CTRL+C to finish. Staying idle..."
    while (can_exit <> True):
        for e in srciplist.keys():
            srciplist[e][2].send(keepalive.pack())
        keepalivetimer=30
        time.sleep(keepalivetimer)

    for e in srciplist.keys():
        srciplist[e][2].close()

    print "Finished!"

signal.signal(signal.SIGTERM, go_down)
signal.signal(signal.SIGINT, go_down)
main()
