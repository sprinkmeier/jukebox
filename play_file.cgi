#!/usr/bin/env python

import os
import cgi
import glob
import time
import cgitb; cgitb.enable()

form = cgi.FieldStorage()
number = form.getvalue('number', None)
letter = form.getvalue('letter', None)

if number and letter:
    with open('/dev/shm/jbq-%d' % int(time.time()),'w') as w:
        w.write(number)
        w.write(' ')
        w.write(letter)
    message = "The file '<em>" + number + letter + "</em>' was enqueued."
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

