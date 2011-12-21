#!/usr/bin/env python

from optparse import OptionParser
from dpkt import bgp
from pybgpdump import BGPDump

DELIMS = ( ('', ''),
           ('{', '}'),  # AS_SET
           ('', ''),    # AS_SEQUENCE
           ('(', ')'),  # AS_CONFED_SEQUENCE
           ('[', ']') ) # AS_CONFED_SET

def path_to_str(path):
    str = ''
    for seg in path.segments:
        str += DELIMS[seg.type][0]
        for AS in seg.path:
            str += '%d ' % (AS)
        str = str[:-1]
        str += DELIMS[seg.type][1] + ' '
    return str

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='input', default='sample.dump.gz',
                      help='read input from FILE', metavar='FILE')
    (options, args) = parser.parse_args()

    dump = BGPDump(options.input)
    for mrt_h, bgp_h, bgp_m in dump:
        path = ''
        for attr in bgp_m.update.attributes:
            if attr.type == bgp.AS_PATH:
                print path_to_str(attr.as_path)
                break

if __name__ == '__main__':
    main()
