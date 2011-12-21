#!/usr/bin/env python

from optparse import OptionParser
from pybgpdump import BGPDump

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='input', default='sample.dump.gz',
                      help='read input from FILE', metavar='FILE')
    (options, args) = parser.parse_args()

    messages = 0
    announced = 0
    withdrawn = 0

    dump = BGPDump(options.input)
    for mrt_h, bgp_h, bgp_m in dump:
        messages += 1
        announced += len(bgp_m.update.announced)
        withdrawn += len(bgp_m.update.withdrawn)

    print '%d total messages with %d announced and %d withdrawn routes' % \
          (messages, announced, withdrawn)

if __name__ == '__main__':
    main()
