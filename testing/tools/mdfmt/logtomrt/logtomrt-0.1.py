####################################################################################                                                        
# Copyright (c) 2009, Centre for Advanced Internet Architectures                                                                            
# Swinburne University of Technology, Melbourne, Australia                                                                                  
# (CRICOS number 00111D).                                                                                                                   
#                                                                                                                                           
####################################################################################                                                        
#                                                                                                                                           
# Log to MRT converter
# Converts Quagga text logfiles to MRT binary dump files
# for further processing. Needs a complete BGP session,
# including OPEN Messages to distinguish between
# 4 byte AS numbers and not.
# Processes only IPv4 Prefixes.
# Requires an 4 byte AS number capable dpkt version. 
# See README-logtomrt for details.
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
# 3. The names of the authors, the "Centre for Advanced Internet Architectures"
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

import dpkt  #AS4 version needed
import struct
import socket
import re
from optparse import OptionParser
import time

states=(("Idle", 1),
            ("Connect", 2), 
            ("Active", 3),
            ("OpenSent", 4),
            ("OpenConfirm", 5),
            ("Established", 6))

# Create state change MRT entry - this is not commonly found in MRT dumps.
def createstatechange(logline, locip, locas, asiptuple):
    mrt=dpkt.mrt.MRTHeader()   # create MRT packet header
    mrt.type=dpkt.mrt.BGP4MP  #set packet type to BGP4MP
    mrt.subtype=dpkt.mrt.BGP4MP_STATE_CHANGE  # set packet subtype to state change type - that's what the packet will be
    m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGP: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*went from (.+) to (.+)", logline) #search for the state change in the text
    if(m):
        oldstate=0
        newstate=0
        for s in states:     # extract information about state transition
            if(m.group(3).strip()==s[0]):
                oldstate=s[1]
            if(m.group(4).strip()==s[0]):
                newstate=s[1]
        mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S"))) # rercod timestamp
        asn=0
        for tup in asiptuple:
            if (tup[0]==m.group(2)):
                asn=tup[1]
        if(asn==0):
            print "Could not find any AS number for IP:"+m.group(2)
            exit(-1)
        afi=dpkt.mrt.AFI_IPv4  # set address family
        iface=0
        # convert remote and local AS number  as well as the interface number (0  as we don't know it) and address family to network  byte order and record as mrt.data
        # Dpkt does not yet have functions for creating state change entries
        mrt.data=struct.pack("!HHHH",asn, locas, iface, afi)  
        mrt.data+=socket.inet_aton(m.group(2))
        mrt.data+=socket.inet_aton(locip)  # add IP address
        mrt.data+=struct.pack("!HH",oldstate, newstate) # add state change information
        mrt.len=len(mrt.data) #record the packet length
    return mrt

# Create a KEEPALIVE packet
def createkeepalive(logline, locip, locas, asiptuple):
    mrt=dpkt.mrt.MRTHeader()
    mrt.type=dpkt.mrt.BGP4MP
    mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
    mrtsub=dpkt.mrt.BGP4MPMessage_32()                      # Create an empty 4 byte AS BGP4MP subtype packet
    mrtsub.dst_ip=struct.unpack('!L',socket.inet_aton(locip))[0]
    mrtsub.dst_as=locas
    mrtsub.intf=0
    mrtsub.family=dpkt.mrt.AFI_IPv4
    m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGP: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*KEEPALIVE rcvd", logline)
    if(m):
        mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S")))
        for tup in asiptuple:
            if (tup[0]==m.group(2)):
                asn=tup[1]
        if(asn==0):
            print "Could not find any AS number for IP:"+m.group(2)
            exit(-1)
        mrtsub.src_as=asn
        mrtsub.src_ip=struct.unpack('!L',socket.inet_aton(m.group(2)))[0]
        mrt.data=mrtsub
        keepalive=dpkt.bgp.BGP(type=dpkt.bgp.KEEPALIVE)  # Create an empty BGP KEEPALIVE packet
        keepalive.len=len(keepalive) # Record the packet length  - KEEEPALIVES do not contain any data
        mrtsub.data=keepalive
    mrt.data=mrtsub
    mrt.len=len(mrtsub)
    return mrt

# Create an OPEN packet
def createopen(logline, locip, locas, asiptuple):
    mrt=dpkt.mrt.MRTHeader()   #Create MRT packet
    mrt.type=dpkt.mrt.BGP4MP
    mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
    mrtsub=dpkt.mrt.BGP4MPMessage_32()  # Create an empty 4 byte AS BGP4MP subtype packet
    mrtsub.dst_ip=struct.unpack('!L',socket.inet_aton(locip))[0]
    mrtsub.dst_as=locas
    mrtsub.intf=0
    mrtsub.family=dpkt.mrt.AFI_IPv4
    bgppkt=dpkt.bgp.BGP()    # Create an empty BGP packet
    openpkt=bgppkt.Open()    # Create an empty OPEN packet
    m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGP: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*rcv OPEN, version ([0-4]), remote-as.* ([0-9]+), holdtime ([0-9]+), id ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*\n.*rcv OPEN w\/ OPTION parameter len: ([0-9]+).*", logline)
    if(m):
        mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S")))
        for tup in asiptuple:
            if (tup[0]==m.group(2)):
                asn=tup[1]
        if(asn==0):
            print "Could not find any AS number for IP:"+m.group(2)
            exit(-1)
        mrtsub.src_as=asn
        mrtsub.src_ip=struct.unpack('!L',socket.inet_aton(m.group(2)))[0]  # Add information to MRT packet
        openpkt.asn=int(m.group(4)) # Add remote AS number 
        openpkt.identifier=struct.unpack('!L',socket.inet_aton(m.group(6)))[0] # Add remote IP address
        openpkt.v=int(m.group(3)) # Add BGP version number
        openpkt.holdtime=int(m.group(5)) # Add holdtime information
        openpkt.param_len=int(m.group(7)) # Add parameter length. This should be  done by calculating the effective length  of the parameters after adding them below. But we trust the log file.
        openpkt.parameters=[]  #Empty array for the parameters
    else:
        return 0
    lines=logline.strip().split("\n")
    openparams=[]
    cap=[]
    i=0
    for e in lines:
        m=re.search(".*rcvd OPEN w\/ optional parameter type ([0-9]+) .* len ([0-9]+).*", e)
        if(m):
            openparams.append(openpkt.Parameter())  # Create empty Parameter container
            openparams[i].type=int(m.group(1)) # Add Parameter type 
            openparams[i].len=int(m.group(2))
        m=re.search(".*capability \(([0-9]+)\), length ([0-9]+).*", e)
        if(m):
            # Create new Capability container. See codes at http://www.iana.org/assignments/capability-codes/capability-codes.xhtml. 
            # Len should  be added through len(cap[i]), but again we know beforehand
            cap.append(openparams[i].Capability(code=int(m.group(1)), len=int(m.group(2)))) 
            openparams[i].data=cap[i]  # Add Capability container to Parameter container
            if(cap[i].code==dpkt.bgp.CAP_SUPPORT_AS4):
                cap[i].data=struct.pack(">L", asn)   # Set 4 byte as number support and encode AS as 4 byte 
                openpkt.parameters.append(openparams[i])
                for tup in asiptuple:
                    if (tup[1]==mrtsub.src_as):
                        tup[2]=1
                i+=1
            elif(not ((cap[i].code==dpkt.bgp.CAP_SUPPORT_AS4) or (cap[i].code==dpkt.bgp.CAP_MULTIPROTOCOL))):
                openpkt.parameters.append(openparams[i])
                i+=1
        m=re.search(".*afi\/safi: ([0-9]+)\/([0-9]+).*", e)
        if(m):
            if(cap[i].code==dpkt.bgp.CAP_MULTIPROTOCOL):
                multi=cap[i].MultiProtocol(afi=int(m.group(1)), res=0, safi=int(m.group(2))) # Create multiprotocol capability container
                cap[i].data=multi  # Add multiprotocol container to capability container
                openpkt.parameters.append(openparams[i]) # Append parameter container to parameter array
                i+=1
            else:
                print "Multi Protocol Capability Error: " + e
                exit(-1)
    bgppkt.data=openpkt.pack() # Pack the OPEN packet container as BGP data
    bgppkt.len=len(bgppkt) # Add BGP packet length information - here we have a usable BGP packet ready to be wired 
    mrtsub.data=bgppkt # Add BGP packet to MRT subpacket
    mrt.data=mrtsub  # Add MRT subpacket to MRT packet
    mrt.len=len(mrtsub) # Add length information
    return mrt

# Create an UPDATE packet  for announcement
def createupdate(prefixlist,locip, locas, asiptuple ):
    as4=0
    asn=0
    line=prefixlist[0]
    mrt=dpkt.mrt.MRTHeader()  # Create MRT container
    mrt.type=dpkt.mrt.BGP4MP
    mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
    mrtsub=dpkt.mrt.BGP4MPMessage_32() # Create MRT subtype container
    mrtsub.dst_ip=struct.unpack('!L',socket.inet_aton(locip))[0]
    mrtsub.dst_as=locas
    mrtsub.intf=0
    mrtsub.family=dpkt.mrt.AFI_IPv4
    bgppkt=dpkt.bgp.BGP(type=dpkt.bgp.UPDATE) # Create BGP packet container. Set packet type to UPDATE - type 4.
    u=bgppkt.Update("\x00\x04\x00\x00\x00\x00\x00\x00") # Create an empty Update packet container. The arguments resolv a small bug.
    u.attributes=[] # Create empty attribute list
    m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGP: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) rcvd UPDATE w/ attr: nexthop ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\, origin ([ie\?])\,(?: community (?P<com>[0-9: ]*)\,)*(?P<atom> atomic-aggregate\,)*(?: aggregated by (?P<aggr>[0-9\. ]*)\,)* path (?P<path>[0-9 ]*)", line)
    if(m):
        mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S")))
        for tup in asiptuple:
            if (tup[0]==m.group(2)):
                asn=tup[1]
                as4=tup[2]
        if(asn==0):
            print "Could not find any AS number for IP:"+m.group(2)
            exit(-1)
        mrtsub.src_as=asn
        mrtsub.src_ip=struct.unpack('!L',socket.inet_aton(m.group(2)))[0] # Add the ne3cessary MRT information to the MRT packet
        # Now  extract update information from log file
        nexthop=m.group(3)
        if(m.group(4)=="i"):
            origin=dpkt.bgp.ORIGIN_IGP
        if(m.group(4)=="e"):
            origin=dpkt.bgp.ORIGIN_EGP
        if(m.group(4)=="?"):
            origin=dpkt.bgp.INCOMPLETE
        community=0
        if(m.group("com")):
            community=m.group("com").strip().split(" ")
        atomicaggr=0
        if(m.group("atom")):
            atomicaggr=m.group("atom")
        aggr=0
        if(m.group("aggr")):
            aggr=m.group("aggr").split(" ")
        pathstr=m.group("path").split(" ")
        path=[]
        set=[]
        for item in pathstr:
            if(item):
                if(item[0]=="{"):
                    set.append(item[1:-1]) # List of AS numbers if it's a set
                    print item[1:-1]
                else:
                    path.append(int(item)) # List of AS numbers if it's a sequence
        an=u.Attribute() # Create empty attribute container. Every Attribute needs to be appended to the attribute list.  This is the nexthop attribute.
        n=an.NextHop(ip=struct.unpack("!L",socket.inet_aton(nexthop))[0])
        an.data=n
        an.type=dpkt.bgp.NEXT_HOP
        an.transitive=1 # This needs to be set by hand unfortunately
        an.len=len(n)
        u.attributes.append(an) # Append nexthoop attribute to attribute list
        ao=u.Attribute()
        o=ao.Origin(type=origin)
        ao.data=o
        ao.len=len(o)
        ao.type=dpkt.bgp.ORIGIN
        ao.transitive=1
        u.attributes.append(ao)
        ah=u.Attribute()
        if (as4):
            h=ah.AS4Path("") # If we advertised AS4 capability we create  an AS4Path container for the AS path
        else:
            h=ah.ASPath("") # otherwise we use a ASPath container
            h.segments=[]
        if (as4):
            s=h.AS4PathSegment() # same for the segments, which do the 4 or 2 byte encoding
        else:
            s=h.ASPathSegment() 
        s.path=s.data=path # record the data (it'a a list)
        s.type=dpkt.bgp.AS_SEQUENCE
        s.len=len(path)
        h.segments.append(s) # add segments to list  
        if(set):
            for el in set:
                as_set=el.split(",")
                if (as4):
                    s=h.AS4PathSegment()
                else :
                    s=h.ASPathSegment()
                s.path=as_set
                s.len=len(s)
                s.type=dpkt.bgp.AS_SET
                h.segments.append(s.pack())
        h.data=h.segments
        ah.data=h
        ah.type=dpkt.bgp.AS_PATH
        ah.transitive=1
        ah.len=len(h)
        u.attributes.append(ah)  # Append ASPath attributes to atttribute list
        ac=u.Attribute()
        if(community):
            c=ac.Communities("") # Create coommunities container
            c.list=[]
            for item in community:
                com=item.split(":")
                cc=c.Community(asn=int(com[0]), value=int(com[1]))
                c.list.append(cc)
            c.data=c.list
            ac.data=c
            ac.type=dpkt.bgp.COMMUNITIES
            ac.transitive=1
            ac.optional=1
            ac.len=len(c)
            u.attributes.append(ac) # Append communities attribute to attribute list
        if(atomicaggr):
            aaa=u.Attribute()
            aaa.type=dpkt.bgp.ATOMIC_AGGREGATE
            aaa.transitive=1
            aaa.len=0
            u.attributes.append(aaa) #  Append atomic aggregate to attribute list. 
        if(aggr):
            aa=u.Attribute()
            aa.type=dpkt.bgp.AGGREGATOR
            aa.transitive=1
            aa.optional=1
            if(as4):
                ag=aa.AS4Aggregator(asn=int(aggr[0]), ip=struct.unpack("!L",socket.inet_aton(aggr[1]))[0]) # Create AS4 Aggregator if AS4 is advertised in OPEN
            else:
                ag=aa.Aggregator(asn=int(aggr[0]), ip=struct.unpack("!L",socket.inet_aton(aggr[1]))[0]) # Create Aggreagtor container
            aa.data=ag
            aa.len=len(ag)
            u.attributes.append(aa) # Append aggregator to attribute list

    # Add prefixes to UPDATE packet
    repr(u)
    prefixlist.remove(line)
    u.announced=[]  # Create empty list for announced prefixes
    u.withdrawn=[] # Create empty list for withdrawn prefixes. This is for safety.
    mrtsub.data=bgppkt 
    mrt.data=mrtsub
    for p in prefixlist:
        r=dpkt.bgp.RouteIPV4() # Create empty IPv4 Prefix container. 
        r.len = int(p[1])
        r.prefix = socket.inet_aton(p[0]) # Add prefix. Needs to be converted to network byte order first.
        u.announced.append(r) # Append prefix to announced list.

    bgppkt.data=u  # Update container is BGP packet data
    bgppkt.len=len(bgppkt) # Calculate BGP packet length
    mrt.len=len(mrtsub) # Calculate MRT packet length
    return mrt

# Create an UPDATE packet  for withdrawal
def createwithdraw(logline, locip, locas, asiptuple):
    mrt=dpkt.mrt.MRTHeader()
    mrt.type=dpkt.mrt.BGP4MP
    mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
    mrtsub=dpkt.mrt.BGP4MPMessage_32()
    mrtsub.dst_ip=struct.unpack('!L',socket.inet_aton(locip))[0]
    mrtsub.dst_as=locas
    mrtsub.intf=0
    mrtsub.family=dpkt.mrt.AFI_IPv4
    bgppkt=dpkt.bgp.BGP(type=dpkt.bgp.UPDATE)
    # Create update contianer and empty lists
    # As it's only a withdrawal, the announced and attributes lists remain empty
    u=bgppkt.Update("\x00\x04\x00\x00\x00\x00\x00\x00")
    u.withdrawn=[]  
    u.announced=[]
    u.attributes=[]
    m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGP: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*rcvd UPDATE about ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\/([0-9]{1,2}) -- withdrawn", logline)
    if(m):
        mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S")))
        for tup in asiptuple:
            if (tup[0]==m.group(2)):
                asn=tup[1]
        if(asn==0):
            print "Could not find any AS number for IP:"+m.group(2)
            exit(-1)
        mrtsub.src_as=asn
        mrtsub.src_ip=struct.unpack('!L',socket.inet_aton(m.group(2)))[0]
        mrt.data=mrtsub
        # Create prefix container and add prefix to withdrawn list
        # Every BGP packet will carry only one withdrawn prefix. This could be optimised.
        r=dpkt.bgp.RouteIPV4() 
        r.len = int(m.group(4))
        r.prefix = socket.inet_aton(m.group(3))
        u.withdrawn.append(r)
        bgppkt.data=u
        bgppkt.len=len(bgppkt)
        mrtsub.data=bgppkt
        mrt.len=len(mrtsub)
        return mrt	

# Create NOTIFICATION packet
def createnotification(logline, locip, locas, asiptuple):
    mrt=dpkt.mrt.MRTHeader()
    mrt.type=dpkt.mrt.BGP4MP
    mrt.subtype=dpkt.mrt.BGP4MP_MESSAGE_32BIT_AS
    mrtsub=dpkt.mrt.BGP4MPMessage_32()
    mrtsub.dst_ip=struct.unpack('!L',socket.inet_aton(locip))[0]
    mrtsub.dst_as=locas
    mrtsub.intf=0
    mrtsub.family=dpkt.mrt.AFI_IPv4
    bgppkt=dpkt.bgp.BGP(type=dpkt.bgp.NOTIFICATION)  
    n=bgppkt.Notification() # Create empty Notification container
    m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGP: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*received NOTIFICATION ([0-9])\/([0-9]{1,2}).*", logline)
    if(m):
        mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S")))
        for tup in asiptuple:
            if (tup[0]==m.group(2)):
                asn=tup[1]
        if(asn==0):
            print "Could not find any AS number for IP:"+m.group(2)
            exit(-1)
        mrtsub.src_as=asn
        mrtsub.src_ip=struct.unpack('!L',socket.inet_aton(m.group(2)))[0]
        mrt.data=mrtsub
        n.code=int(m.group(3)) # Add notification code
        n.subcode=int(m.group(4)) # Add notification subcode
        bgppkt.data=n
        bgppkt.len=len(bgppkt) # Calculate BGP packet length
        mrtsub.data=bgppkt # Calculate MRT packet length
        mrt.len=len(mrtsub)
        return mrt

 # Main function -  contains the parsing logic
def main():
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
        
    as4=0

    parser = OptionParser()
    parser.add_option("-l", "--logfile", dest="logfile",default=0, 
                  help="quagga text log file")
    parser.add_option("-m", "--mrtfile",  dest="mrtfile", default=0, 
                  help="output mrt file")
    parser.add_option("-a", "--asip",  dest="asipfile", default=0, 
                  help="file containing the IP to AS mapping. The file may consist only of an IP address followed by an AS number per line. All additional entries are ignored")
    parser.add_option("-i", "--ip",  dest="locip", default=0, 
                  help="ip of the router that produced the logfile. The IP to AS number mapping is also needed in the mapping file")
    (options, args) = parser.parse_args()
    asiptuple=[]
    locip=""
    locas=0
    
    if(not options.logfile or not options.mrtfile or not options.asipfile or not options.locip):
        parser.print_help()
        exit(-1)
    
    f=open(options.logfile, "r")
    asip=open(options.asipfile, "r")
    mfile=open(options.mrtfile, "w")
    locip=options.locip.strip()
    
    # Parse the AS number to IP address file. This is needed for a proper MRT file creation.
    for l in asip:
        m=re.search("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})[\s]*(?:(?P<asn>[0-9]+)|(?P<asdot>[0-9]+\.[0-9]+))", l)
        if(m):
            asn=0
            if(m.group("asn")):
                asn=int(m.group("asn"))
                if((asn>=(2**32)-1) or (asn<1) or (65535<=asn<131072)):
                    print "Invalid AS Number in file: "+asipfile
                    exit(-1)
            if(m.group("asdot")):
                tuple=m.group("asdot").split("\.")
                mul=int(tuple[0])
                add=int(tuple[1])
                if((2>mul>65535) or (not mul) or (mul==65535 and add==65535) or (0>=add>65536) or (not add)):
                    print "Invalid AS Number in file: "+asipfile
                    exit(-1)
                asn=(mul*65536)+add
            if(m.group(1)==locip):
                locas=asn
            else:
                asiptuple.append([m.group(1), asn,  0])
    asip.close()
     
    # Start parsing the text log file
    lineblock=""
    prefixlist=[]
    for line in f:
        # Create an MRT start entry (type 1) - might be unnecessary
        m=re.search("([0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*BGPd.*starting:.*", line)
        if(m):
            mrt=dpkt.mrt.MRTHeader()
            mrt.ts=int(time.mktime(time.strptime(m.group(1),"%Y/%m/%d %H:%M:%S")))
            mrt.type=1
            mrt.subtype=0
            mrt.len=0
            mfile.write(mrt.pack())
        # Parse state changes - calls "createstatechange" function
        m=re.search(".*went from.*to", line)
        if(m):
            mrt=createstatechange(line, locip, locas, asiptuple)
            mfile.write(mrt.pack())
        # Parse KEEPALIVE entries - calls "createkeepalive" function
        m=re.search(".*KEEPALIVE rcvd.*", line)
        if(m):
            mrt=createkeepalive(line, locip, locas, asiptuple)
            if(mrt):
                mfile.write(mrt.pack())
        # Parse the OPEN packet - calls "createopen" function
        # Performs some more complicted regular expression searches
        # to find all parameters
        m=re.search(".*rcv OPEN, version.*", line)
        if(m):
            lineblock=lineblock+line.strip()+"\n"
        if(lineblock and not(lineblock ==  (line.strip()+"\n"))):
            m=re.search(".*OPEN.*", line)
            if(m):
                m=re.search(".*\[FSM\].*", line)
                if(not m):
                    lineblock=lineblock+line.strip()+"\n"
            else:
                m=re.search(".*BGP: message index.*", line)
                if(not m):
                    mrt=createopen(lineblock, locip, locas, asiptuple)
                    if(mrt):
                        mfile.write(mrt.pack())
                    lineblock=""
        # Parse the UPDATE annnouce packet and pack all prefixes into one packet
        # The logfile contain s only as many prefixes per UPDATE message 
        # as fit into a single BGP packet.
        if(prefixlist):
            m=re.search(".* rcvd ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\/([0-9]{1,2}).*", line)
            if(m):
                prefixlist.append((m.group(1), m.group(2)))
            else:
                mrt=createupdate(prefixlist, locip, locas, asiptuple)
                if(mrt):
                    mfile.write(mrt.pack())
                prefixlist=[]
        m=re.search(".*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*rcvd UPDATE w/ attr: nexthop.*", line)
        if(m):
            prefixlist.append(line)
        # Parse withdrawals
        m=re.search(".* rcvd UPDATE about.*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*withdrawn", line)
        if(m):
            mrt=createwithdraw(line, locip, locas, asiptuple)
            if(mrt):
                mfile.write(mrt.pack())
        # Parse notifications
        m=re.search(".*BGP:.*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*received NOTIFICATION.*", line)
        if(m):
            mrt=createnotification(line, locip, locas, asiptuple)
            if(mrt):
                mfile.write(mrt.pack())

    f.close() # Close the text log file
    mfile.close() # Close the MRT file

main()
