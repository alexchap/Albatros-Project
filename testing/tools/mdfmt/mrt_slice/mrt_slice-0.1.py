####################################################################################
# Copyright (c) 2009, Centre for Advanced Internet Architectures
# Swinburne University of Technology, Melbourne, Australia
# (CRICOS number 00111D).
#
####################################################################################
#
# MRT slice: Tool for cutting out slices of a large MRT dump, 
# using MRT RIB dumps to create updates for the initial RIB 
# propagation of a BGP session.
# Requires an 4 byte AS number and TableDumpV2 capable dpkt version.
# See README-mrtslice for details.
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
import struct
import socket
import re
import time
from optparse import OptionParser

def main():
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
        

    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="indump",default=0, action="store", 
                  help="MRT input dump file", metavar="DUMPFILE")
    parser.add_option("-o", "--outfile",  dest="outdump", default=0, action="store", 
                  help="MRT output dump file", metavar="DUMPFILE")
    parser.add_option("-r", "--ribdump",  dest="ribdump", default=0, action="store", 
                  help="MRT RIB dump file (TableDump_v2). The new MRT dump file will start from the time of the first RIB dump entry. If not set, the slice will start from the beginning of the input dump file", metavar="RIBDUMP")
    parser.add_option("-t", "--timespan",  dest="timespan", default="1h",type="string", action="store", 
                    help="Timespan of the slice in seconds. Add \"m\" for minutes, \"h\" for hours, \"d\" for days and \"w\" for weeks. Default is 1 hour (1h)")
    (options, args) = parser.parse_args()
    
    dump=0
    out=0
    rib=0
    rib_type=0
    
    slicetime=0
    starttime=0
    endtime=0
    
    mrth=0
    mrt_h=0
    
    # Check all command line options for validity
    if (options.indump==0):
        parser.error("No input file given!")
    else:
        dump=open(options.indump, "r")
        if (not dump):
            parser.error("Could not open input file for reading")
        try:
            mrth=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
        except dpkt.dpkt.NeedData:
            parser.error("Input file appears not to be a valid MRT dump")
        if (mrth.type==dpkt.mrt.START):
            mrth=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
        if (mrth.type!=dpkt.mrt.BGP4MP):
            parser.error("Input file is not a valid MRT Update dump (BGP4MP)")
        else:
            starttime=mrth.ts
        dump.close()
    if(options.outdump==0):
        parser.error("No output file given")
    else:
        out=open(options.outdump, "w")
        if (not out):
            parser.error("Could not open output file for writing")
    # Parse the timespan string
    m=re.search("([0-9]+)([mhdw]*)", options.timespan)
    if(m):
        slicetime=int(m.group(1))
        if (m.group(2) == "m" ):
                slicetime=slicetime*60
        if (m.group(2) == "h" ):
                slicetime=slicetime*60*60
        if (m.group(2) == "d" ):
                slicetime=slicetime*60*60*24
        if (m.group(2) == "w" ):
                slicetime=slicetime*60*60*24*7
    else:
        parser.error("Error in timespan input")
    if (options.ribdump!=0):
        rib=open(options.ribdump, "r")
        if (not rib):
            parser.error("Error opening ribdump file for reading")
        else:
            try:
                mrth=dpkt.mrt.MRTHeader(rib.read(dpkt.mrt.MRTHeader.__hdr_len__))
            except dpkt.dpkt.NeedData:
                parser.error("Ribdump file appears not to be a valid MRT dump")
            if (mrth.type!=dpkt.mrt.TABLE_DUMP and mrth.type!=dpkt.mrt.TABLE_DUMP_V2):
                parser.error("Ribdump file is not a valid TABLE_DUMP or TABLE_DUMP_V2 RIB dump")
            else:
                rib_type=mrth.type
                starttime=mrth.ts
 
    
    #Print the start and endtime in human readable format
    endtime=starttime+slicetime
    print "Extracting "+ str(slicetime) +" seconds MRT data from \"" + options.indump + "\"."
    print "Start time is: " + time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(starttime)) + " (" + str(starttime) +")."
    print "End time is: " + time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(endtime))+ " (" + str(endtime)+")." 
    
    updates=0 # variable to count the amount of processed update messages from update dump
    
    # Check whether we use a MRT RIB dump to start 
    # or whether we start from the beginning of the original MRT file
    # We have a RIB dump, so let's start with that
    if(rib!=0):
        dump=open(options.indump, "r")
        peerindex=0
        if(rib_type==dpkt.mrt.TABLE_DUMP_V2):
            # Extract the MRT packet
            while (mrth.subtype!=dpkt.mrt.TABLE_DUMP_V2_PEER_INDEX_TABLE):
                rib.read(mrth.len)
                mrth=dpkt.mrt.MRTHeader(rib.read(dpkt.mrt.MRTHeader.__hdr_len__))
            # first entry must be the peer index table
            peerindex=dpkt.mrt.TableDump2_PeerIndex(rib.read(mrth.len))
        
        count=0 # variable to count the amount of processed prefixes
        
        # Extract the prefixes from the RIB 
        # We create one BGP message for each prefix for simplicity. This can be optimised
        if(rib_type==dpkt.mrt.TABLE_DUMP_V2):
            mrth=dpkt.mrt.MRTHeader(rib.read(dpkt.mrt.MRTHeader.__hdr_len__))
        while (mrth):
            count=count+1
            #print('mrt hdr %d %d' % (mrth.type,mrth.subtype))
            if(rib_type==dpkt.mrt.TABLE_DUMP):
                # Create IPv4 messages
                if(mrth.subtype==dpkt.mrt.AFI_IPv4):
                    ribv4=dpkt.mrt.TableDump(rib.read(mrth.len))
                    #print('ribv4 %d %d %s %d %d' % (ribv4.peer_as,ribv4.peer_ip,str(ribv4.attributes),ribv4.prefix_len,ribv4.prefix))
                    #if(ribv4.prefix!=0):
                    # Create MRT, BGP4MP and BGP packet
                    mrt=dpkt.mrt.MRTHeader()
                    mrt.type=dpkt.mrt.BGP4MP
                    mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
                    mrt.ts=mrth.ts
                    mrtsub=dpkt.mrt.BGP4MPMessage_32()
                    mrtsub.dst_ip=0
                    mrtsub.dst_as=0
                    mrtsub.intf=0
                    mrtsub.src_as=ribv4.peer_as
                    mrtsub.src_ip=ribv4.peer_ip
                    bgppkt=dpkt.bgp.BGP(type=dpkt.bgp.UPDATE)
                    # Create Update container
                    u=bgppkt.Update("\x00\x04\x00\x00\x00\x00\x00\x00")
                    # Add attributes from RIB entry
                    u.attributes=ribv4.attributes
                    # Add prefix from RIB entry
                    r=dpkt.bgp.RouteIPV4()
                    r.len = ribv4.prefix_len
                    r.prefix = struct.pack(">I", ribv4.prefix)
                    # Append prefix to announced list
                    u.announced.append(r)
                    # Create empty withdrawn list for safety
                    u.withdrawn=[]
                    # Add all container to the parent container,
                    # calculate length, pack, and write to file
                    mrtsub.data=bgppkt
                    mrt.data=mrtsub
                    bgppkt.data=u
                    bgppkt.len=len(bgppkt)
                    mrt.len=len(mrtsub)
                    out.write(mrt.pack())
                    #    if(count==500):
                    #        break
                if (mrth.subtype==dpkt.mrt.AFI_IPv6):
                    print "IPv6 not supported!"

            if(rib_type==dpkt.mrt.TABLE_DUMP_V2):
                # Create IPv4 messages
                if (mrth.subtype==dpkt.mrt.TABLE_DUMP_V2_RIB_IPV4_UNICAST or mrth.subtype==dpkt.mrt.TABLE_DUMP_V2_RIB_IPV4_MULTICAST):
                    ribv4=dpkt.mrt.TableDump2_IPV4(rib.read(mrth.len))
                    for i in xrange(ribv4.entry_count):
                        # Create MRT, BGP4MP and BGP packet
                        mrt=dpkt.mrt.MRTHeader()
                        mrt.type=dpkt.mrt.BGP4MP
                        mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
                        mrt.ts=mrth.ts
                        mrtsub=dpkt.mrt.BGP4MPMessage_32()
                        mrtsub.dst_ip=peerindex.id
                        mrtsub.dst_as=0
                        mrtsub.intf=0
                        mrtsub.src_as=peerindex.peers[ribv4.data[i].peer_index].asn
                        mrtsub.src_ip=struct.unpack("!L",socket.inet_aton(peerindex.peers[ribv4.data[i].peer_index].address))[0]
                        bgppkt=dpkt.bgp.BGP(type=dpkt.bgp.UPDATE)
                        # Create Update container
                        u=bgppkt.Update("\x00\x04\x00\x00\x00\x00\x00\x00")
                        # Add attributes from RIB entry
                        u.attributes=ribv4.data[i].attributes
                        # Add prefix from RIB entry
                        r=dpkt.bgp.RouteIPV4()
                        r.len = ribv4.prefix_len
                        r.prefix = ribv4.prefix
                        # Append prefix to announced list
                        u.announced.append(r)
                        # Create empty withdrawn list for safety
                        u.withdrawn=[]
                        # Add all container to the parent container,
                        # calculate length, pack, and write to file
                        mrtsub.data=bgppkt
                        mrt.data=mrtsub
                        bgppkt.data=u
                        bgppkt.len=len(bgppkt)
                        mrt.len=len(mrtsub)
                        out.write(mrt.pack())
                # Create IPv6 messages
                if (mrth.subtype==dpkt.mrt.TABLE_DUMP_V2_RIB_IPV6_UNICAST or mrth.subtype==dpkt.mrt.TABLE_DUMP_V2_RIB_IPV6_MULTICAST):
                    ribv6=dpkt.mrt.TableDump2_IPV6(rib.read(mrth.len))
                    for i in xrange(ribv6.entry_count):
                        mrt=dpkt.mrt.MRTHeader()
                        mrt.type=dpkt.mrt.BGP4MP
                        mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
                        mrt.ts=mrth.ts
                        mrtsub=dpkt.mrt.BGP4MPMessage_32()
                        mrtsub.dst_ip=peerindex.id
                        mrtsub.dst_as=0
                        mrtsub.intf=0
                        mrtsub.src_as=peerindex.peers[ribv6.data[i].peer_index].asn
                        mrtsub.src_ip=struct.unpack("!L",socket.inet_aton(peerindex.peers[ribv6.data[i].peer_index].address))[0]
                        bgppkt=dpkt.bgp.BGP(type=dpkt.bgp.UPDATE)
                        u=bgppkt.Update("\x00\x04\x00\x00\x00\x00\x00\x00")
                        u.attributes=ribv6.data[i].attributes
                        # Create IPv6 prefix container
                        r=dpkt.bgp.RouteIPV6()
                        r.len = ribv6.prefix_len
                        r.prefix = ribv6.prefix
                        u.announced.append(r)
                        u.withdrawn=[]
                        mrtsub.data=bgppkt
                        mrt.data=mrtsub
                        bgppkt.data=u
                        bgppkt.len=len(bgppkt)
                        mrt.len=len(mrtsub)
                        out.write(mrt.pack())
            
            # Insert UPDATE messages from original file
            # after one second of MRT recorded time
            # if the RIB dump spans more than one second
            # This should  be hardly needed
            old_ts=mrth.ts
            try:
                mrth=dpkt.mrt.MRTHeader(rib.read(dpkt.mrt.MRTHeader.__hdr_len__))
            except dpkt.dpkt.NeedData:
                break
            if(mrth.ts>old_ts):
                if not mrt_h:
                    temp = dump.read(dpkt.mrt.MRTHeader.__hdr_len__)
                    if len(temp) < dpkt.mrt.MRTHeader.__hdr_len__ :
                        break
                    mrt_h=dpkt.mrt.MRTHeader(temp)
                while mrt_h.type != dpkt.mrt.BGP4MP:
                    temp = dump.read(dpkt.mrt.MRTHeader.__hdr_len__)
                    if len(temp) < dpkt.mrt.MRTHeader.__hdr_len__ :
                        break
                    mrt_h=dpkt.mrt.MRTHeader(temp)
                while (mrt_h.ts<old_ts):
                    dump.read(mrt_h.len)
                    s=dump.read(dpkt.mrt.MRTHeader.__hdr_len__)
                    if len(s)<dpkt.mrt.MRTHeader.__hdr_len__:
                        break
                    mrt_h=dpkt.mrt.MRTHeader(s)
                while (mrt_h.ts==old_ts):
                    out.write(mrt_h.pack())
                    out.write(dump.read(mrt_h.len))
                    updates=updates+1
                    temp = dump.read(dpkt.mrt.MRTHeader.__hdr_len__)
                    if len(temp) < dpkt.mrt.MRTHeader.__hdr_len__ :
                        break
                    mrt_h=dpkt.mrt.MRTHeader(temp)

        # Finished adding RIB entries,  now proceed with update messages
        rib.close()
        print str(count) + " RIB entries converted to update messages - adding update data.."
        # Read MRT header for the timestamp, don't touch the rest.
        if not mrt_h:
            mrt_h=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
        print str(mrt_h.ts) + " " + str(mrth.ts)
        while (mrt_h.ts<mrth.ts):
            while mrt_h.type != dpkt.mrt.BGP4MP:
                temp = dump.read(dpkt.mrt.MRTHeader.__hdr_len__)
                if len(temp) < dpkt.mrt.MRTHeader.__hdr_len__ :
                    break
                mrt_h=dpkt.mrt.MRTHeader(temp)
            dump.read(mrt_h.len)
            mrt_h=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
        while (mrt_h.ts>=mrth.ts and mrt_h.ts<=endtime):
            while mrt_h.type != dpkt.mrt.BGP4MP:
                temp = dump.read(dpkt.mrt.MRTHeader.__hdr_len__)
                if len(temp) < dpkt.mrt.MRTHeader.__hdr_len__ :
                    break
                mrt_h=dpkt.mrt.MRTHeader(temp)
            out.write(mrt_h.pack())
            out.write(dump.read(mrt_h.len))
            updates=updates+1
            mrt_h=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
        print str(updates) + " update messages added. File: " + options.outdump + " is ready to use."
        dump.close()
        out.flush()
        out.close()
    # If there is no RIB dump, start from the beginning of the original MRT file
    # Must contain a valid RIB propagation sequence to create a useable 
    # set of updates
    else:
        dump=open(options.indump, "r")
        mrth=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
        while (mrth.ts<=endtime):
            out.write(mrth.pack())
            out.write(dump.read(mrth.len))
            mrth=dpkt.mrt.MRTHeader(dump.read(dpkt.mrt.MRTHeader.__hdr_len__))
            print mrth.ts
        dump.close()
        out.flush()
        out.close()
    
if __name__ == "__main__":
    main()
