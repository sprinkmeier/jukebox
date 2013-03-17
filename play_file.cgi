#!/usr/bin/env python

import cgi
import cgitb
import collections
import glob
import os
import socket
import string
import sys
import time

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

    message='<table border="1">\n'


    URL_FMT = "http://%s:%s/%s?number=%%s&letter=%%s" % (
        os.environ['SERVER_NAME'],
        os.environ['SERVER_PORT'],
        os.environ['SCRIPT_NAME'])

    message += "<!-- %s -->\n" % URL_FMT

    for file in files:
        (letter, number, name) = tuple(file.split('/')[-3:])
        url = URL_FMT % (letter, number)
	message += ('<tr><td>%s</td><td>%s</td><td><a href="%s">%s</a></td></tr>\n' % (letter, number, url, name))


    message += "</table>\n"

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
<!-- <p><a href="/">back...</a></p> -->
</body></html>
""" % (message,)
