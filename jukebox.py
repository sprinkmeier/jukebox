#!/usr/bin/env python

import socket
import sys
import os
import traceback

PORT = 55555

# Create a UDP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
sock.bind(('0.0.0.0', PORT))

while True:
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(4096)

    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data

    (letter, number) = data.split()

    try:
        os.system("play /var/jukebox/%s/%s/*" % (letter, number))
    except:
        trace_back.print_exc()

#    if data:
#        sent = sock.sendto(data, address)
#        print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)

