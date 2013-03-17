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
try:
    upload = form['file']
except:
    upload = None

def sanitize_filename(fname):
    sane = set(string.letters + string.digits + '-_.')
    return ''.join(c for c in fname if c in sane)

def uploadFile(upload, letter, number):
    if upload is None:      return ''
    if not upload.filename: return ''

    name    = sanitize_filename(os.path.basename(upload.filename))
    outDir  = os.path.join('/var/jukebox', letter, number)

    try:
        os.makedirs(outDir)
    except:
        pass

    old = glob.glob(os.path.join(outDir,'*'))
    for o in old:
        os.unlink(o)

    outName = os.path.join(outDir, name)
    out = open(outName, 'wb')
    message = "The file '<em>" + name + "</em>' was uploaded successfully to <em>" + outName + "</em>"

    #message += repr(old)

    while True:
        packet = upload.file.read(16 * 1024)
        #message += ' ' + str(len(packet))
        if not packet:
            break
        out.write(packet)
    out.close()


#    os.system('mp3gain "' + outName + '" 2>&1 > /dev/null ')

    return message


def enqueue(letter, number):
    if not letter: return ''
    if not number: return ''
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if not sock: return ''
    message = letter + ' ' + number
    sent = sock.sendto(message, ADDRESS)
    return "The file '<em>" + message + "</em>' was enqueued: " + str(sent)

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
