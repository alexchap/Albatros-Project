#!/usr/bin/env python

import sys, time
from optparse import OptionParser
from dpkt import bgp
from pybgpdump import BGPDump
import dnet

def aspath_to_str(as_path):
    str = ''
    for seg in as_path.segments:
        if seg.type == bgp.AS_SET:
            start = '['
            end = '] '
        elif seg.type == bgp.AS_SEQUENCE:
            start = ''
            end = ' '
        else:
            start = '?%d?' % (seg.type)
            end = '? '
        str += start
        for AS in seg.path:
            str += '%d ' % (AS)
        str = str[:-1]
        str += end
    str = str[:-1]
    return str

def origin_to_str(origin):
    str = ''
    if origin.type == bgp.ORIGIN_IGP:
        str = 'IGP'
    elif origin.type == bgp.ORIGIN_EGP:
        str = 'EGP'
    elif origin.type == bgp.INCOMPLETE:
        str = 'INCOMPLETE'
    return str

def communities_to_str(communities):
    str = ''
    for comm in communities.list:
        try:
            str += '%d:%d ' % (comm.asn, comm.value)
        except AttributeError:
            str += '%d ' % (comm.value)
    str = str[:-1]
    return str

def clusterlist_to_str(cluster_list):
    str = ''
    for cluster in cluster_list.list:
        str += '%s ' % dnet.ip_ntoa(cluster)
    str = str[:-1]
    return str

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='input', default='sample.dump.gz',
                      help='read input from FILE', metavar='FILE')
    parser.add_option("-m", "--machine", action="store_true", dest="machine",
                      default=False, help="output in machine-readable form")
    (options, args) = parser.parse_args()

    out = sys.stdout.write
    dump = BGPDump(options.input)

    if options.machine:
        for mrt_h, bgp_h, bgp_m in dump:
            next_hop = 'none'
            atomic_aggregate = 'NAG'
            local_pref = multi_exit_disc = '0'
            origin = as_path = communities = aggregator = ''

            for attr in bgp_m.update.attributes:
                if attr.type == bgp.AS_PATH:
                    as_path = aspath_to_str(attr.as_path)
                elif attr.type == bgp.ORIGIN:
                    origin = origin_to_str(attr.origin)
                elif attr.type == bgp.NEXT_HOP:
                    next_hop = dnet.ip_ntoa(attr.next_hop.ip)
                elif attr.type == bgp.LOCAL_PREF:
                    local_pref = '%d' % (attr.local_pref.value)
                elif attr.type == bgp.MULTI_EXIT_DISC:
                    multi_exit_disc = '%d' % (attr.multi_exit_disc.value)
                elif attr.type == bgp.COMMUNITIES:
                    communities = communities_to_str(attr.communities)
                elif attr.type == bgp.ATOMIC_AGGREGATE:
                    atomic_aggregate = 'AG'
                elif attr.type == bgp.AGGREGATOR:
                    aggregator = dnet.ip_ntoa(attr.aggregator.ip)

            time_str = '%s|%s' % ('BGP4MP', mrt_h.ts)

            attrs = '%s|%s|%s|%s|%s|%s|%s|%s|' % \
                    (as_path, origin, next_hop, local_pref, multi_exit_disc,
                     communities, atomic_aggregate, aggregator)

            for route in bgp_m.update.announced:
                out('%s|A|%s|%d|%s/%d|%s\n' % 
                    (time_str, dnet.ip_ntoa(bgp_h.src_ip), bgp_h.src_as,
                     dnet.ip_ntoa(route.prefix), route.len, attrs))

            for route in bgp_m.update.withdrawn:
                out('%s|W|%s|%d|%s/%d\n' % 
                    (time_str, dnet.ip_ntoa(bgp_h.src_ip), bgp_h.src_as,
                     dnet.ip_ntoa(route.prefix), route.len))
    else:
        for mrt_h, bgp_h, bgp_m in dump:
            origin = as_path = next_hop = multi_exit_disc = local_pref = \
            atomic_aggregate = aggregator = originator_id = cluster_list = \
            communities = None
            for attr in bgp_m.update.attributes:
                if attr.type == bgp.ORIGIN:
                    origin = origin_to_str(attr.origin)
                elif attr.type == bgp.AS_PATH:
                    as_path = aspath_to_str(attr.as_path)
                elif attr.type == bgp.NEXT_HOP:
                    next_hop = dnet.ip_ntoa(attr.next_hop.ip)
                elif attr.type == bgp.MULTI_EXIT_DISC:
                    multi_exit_disc = '%d' % (attr.multi_exit_disc.value)
                elif attr.type == bgp.LOCAL_PREF:
                    local_pref = '%d' % (attr.local_pref.value)
                elif attr.type == bgp.ATOMIC_AGGREGATE:
                    atomic_aggregate = 'AG'
                elif attr.type == bgp.AGGREGATOR:
                    aggregator = 'AS%d %s' % \
                                 (attr.aggregator.asn,
                                  dnet.ip_ntoa(attr.aggregator.ip))
                elif attr.type == bgp.ORIGINATOR_ID:
                    originator_id = dnet.ip_ntoa(attr.originator_id.value)
                elif attr.type == bgp.CLUSTER_LIST:
                    cluster_list = clusterlist_to_str(attr.cluster_list)
                elif attr.type == bgp.COMMUNITIES:
                    communities = communities_to_str(attr.communities)

            out('TIME: %s\n' %
                (time.strftime('%D %T', time.localtime(mrt_h.ts))))
            out('TYPE: BGP4MP/MESSAGE/Update\n')
            out('FROM: %s AS%d\n' % (dnet.ip_ntoa(bgp_h.src_ip), bgp_h.src_as))
            out('TO: %s AS%d\n' % (dnet.ip_ntoa(bgp_h.dst_ip), bgp_h.dst_as))
            if origin:
                out('ORIGIN: %s\n' % (origin))
            if as_path:
                out('ASPATH: %s\n' % (as_path))
            if next_hop:
                out('NEXT_HOP: %s\n' % (next_hop))
            if multi_exit_disc:
                out('MULTI_EXIT_DISC: %s\n' % (multi_exit_disc))
            if local_pref:
                out('LOCAL_PREF: %s\n' % (local_pref))
            if atomic_aggregate:
                out('ATOMIC_AGGREGATE\n')
            if aggregator:
                out('AGGREGATOR: %s\n' % (aggregator))
            if originator_id:
                out('ORIGINATOR_ID: %s\n' % (originator_id))
            if cluster_list:
                out('CLUSTER_LIST: %s\n' % (cluster_list))
            if communities:
                out('COMMUNITY: %s\n' % (communities))

            if len(bgp_m.update.announced) > 0:
                out('ANNOUNCE\n')
                for route in bgp_m.update.announced:
                    out('  %s/%d\n' % (dnet.ip_ntoa(route.prefix), route.len))

            if len(bgp_m.update.withdrawn) > 0:
                out('WITHDRAW\n')
                for route in bgp_m.update.withdrawn:
                    out('  %s/%d\n' % (dnet.ip_ntoa(route.prefix), route.len))

            out('\n')

if __name__ == '__main__':
    main()
