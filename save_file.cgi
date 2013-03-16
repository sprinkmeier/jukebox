#!/usr/bin/env python

import cgi
import cgitb; cgitb.enable()
import glob
import os
import string

form = cgi.FieldStorage()
letter = form.getvalue('letter')
number = form.getvalue('number')
upload = form['file']


def sanitize_filename(fname):
    sane = set(string.letters + string.digits + '-_.')
    return ''.join(c for c in fname if c in sane)

if upload.filename:
    name    = sanitize_filename(os.path.basename(upload.filename))
#    name    = os.path.basename(upload.filename)
    outDir  = os.path.join('/var/jukebox', letter, number)
    try:
        os.makedirs(outDir)
    except:
        pass
    outName = os.path.join(outDir, name)
    out = open(outName, 'wb')
    message = "The file '<em>" + name + "</em>' was uploaded successfully to <em>" + outName + "</em>"
    old = glob.glob(os.path.join(outDir,'*'))

    while True:
        packet = upload.file.read(1000)
        if not packet:
            break
        out.write(packet)
    out.close()
    for o in old:
        if o == outName: continue
	os.unlink(o)
else:

    message = "Derp... could you try that again please?"

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
<p><a href="/">back...</a></p>
</body></html>
""" % (message,)

