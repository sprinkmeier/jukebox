#!/usr/bin/env python

import os
import cgi
import glob
import time
import cgitb
import socket
import sys

PORT    = 55555
ADDRESS = ('localhost', PORT)

cgitb.enable()


form = cgi.FieldStorage()
number = form.getvalue('number', None)
letter = form.getvalue('letter', None)

if number and letter:
    # Create a UDP socket
#    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if sock:
        message = number + ' ' + letter
        sent = sock.sendto(message, ADDRESS)
        message = "The file '<em>" + message + "</em>' was enqueued: " + str(sent)

else:
    files = sorted(glob.glob('/var/jukebox/*/*/*'))

    message='<table border="1">'

    for file in files:
        lnn = tuple(file.split('/')[-3:])
	message += ("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % lnn)

    message += "</table>"

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
<p><a href="/">back...</a></p>
</body></html>
""" % (message,)

