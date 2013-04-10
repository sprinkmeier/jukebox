#!/usr/bin/env python

import cgi
import cgitb
import collections
import csv
import glob
import json
import os
import socket
import string
import sys
import time
import traceback

LETTERS = "ABCDEFGHJKLMNPQRSTUV"

PORT    = 55555
ADDRESS = ('localhost', PORT)

cgitb.enable()

title = 'Jukebox'

form = cgi.FieldStorage()
number = form.getvalue('number', None)
letter = form.getvalue('letter', None)
submit = form.getvalue('submit', None)
chk    = form.getvalue('chk', None)

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

    while True:
        packet = upload.file.read(64 * 1024)
        if not packet:
            break
        out.write(packet)
    out.close()

#    os.system('mp3gain "' + outName + '" 2>&1 > /dev/null ')

    return message

def sendUDP(msg):
    if msg in LETTERS:
        for i in range(8):
            sendUDP(msg + " " + str(i+1))
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock.sendto(msg, ADDRESS)


def process(submit, letter, number):
    if not submit: return ''
    sendUDP(submit)

    if not letter: return ''
    if not number: return ''

    message = letter + ' ' + number
    outDir  = os.path.join('/var/jukebox', letter, number)

    if submit == "Delete":
        os.system("rm %s/*" % outDir)
        return "The file '<em>" + message + "</em>' was deleted"

    # Create a UDP socket
    sent = sendUDP(message)

    return "The file '<em>" + message + "</em>' was enqueued: " + str(sent)

def fileList():
    ret = collections.defaultdict(dict)

    for fn in sorted(glob.glob('/var/jukebox/[A-Z]/*/*')):
        (fn, name)   = os.path.split(fn)
        (fn, number) = os.path.split(fn)
        (fn, letter) = os.path.split(fn)
        ret[letter][int(number)] = name

    return dict(ret)

def playlist(files):
    if chk:
        delBtn = '<input type="submit" name="submit" value="Delete">'
    else:
        delBtn = ''
    message = '<table border="1">\n'

#    URL_FMT = "http://%s:%s/%s?letter=%%s&number=%%d" % (
#        os.environ['SERVER_NAME'],
#        os.environ['SERVER_PORT'],
#        os.environ['SCRIPT_NAME'])
#    message += "<!-- %s -->\n" % URL_FMT

    BTNS_FMT = """<form action="%s" method="post">
    <input type=hidden name='letter' value='{letter}'>
    <input type=hidden name='number' value='{number}'>
    <input type="submit" name="submit" value="Play">
    %s
</form>""" %  (os.environ['SCRIPT_NAME'],delBtn)

    for letter in sorted(files):
        d = files[letter]
        col1 = '<td rowspan="%d" id="letter_%s">%s</td>' % (len(d), letter, button(letter))
        for number in sorted(d):
            name = "<a href='/jukebox/%s/%d/%s'>%s</a>" % (letter, number, d[number],d[number])
            message += ("""<TR>
    %s
    <td>%d</td>
    <td><em>%s</em></td>
    <td>%s</td>
</TR>\n""" % (
                    col1, number, name,#d[number],
                    BTNS_FMT.format(letter = letter, number = number)))
            col1=''

    message += "</table>\n"

    return message

def uploader(files):

    selected = ('A', 1)
    for letter in reversed(LETTERS):
        if letter not in files:
            selected = (letter, 1)
            continue
        numbers = set(range(1,9)).difference(set(files[letter]))
        if numbers:
            selected = (letter, min(numbers))

    letters = ''

    for letter in LETTERS:
        if letter == selected[0]:
            letters += '<option value="%s" selected>%s</option>\n' % (letter, letter)
        else:
            letters += '<option value="%s">%s</option>\n' % (letter, letter)

    numbers = ''
    for number in range(1,9):
        if number == selected[1]:
            numbers += '<option value="%s" selected>%s</option>\n' % (number, number)
        else:
            numbers += '<option value="%s">%s</option>\n' % (number, number)

    message = """

    <form enctype="multipart/form-data" action="%s" method="post">
        <select name="letter">
            %s
        </select>
        <select name="number">
            %s
        </select>
        <p>File: <input type="file" name="file"></p>
        <p><input type="submit" value="Upload"></p>
    </form>
""" % (os.environ['SCRIPT_NAME'], letters, numbers)


    return message

def button(name, extra = ""):
    return """
   <form enctype="multipart/form-data" action="%s" method="post">
        <input type="submit" name="submit" value="%s">
        %s
    </form>
""" % (os.environ['SCRIPT_NAME'], name, extra)


def buttons():
    message  = "<table><tr><td>"
    message += "</td><td>".join((button("Stop"),
                                 button("Flush"),
                                 button("Shutdown"),
                                 button("Refresh","""<input type="checkbox" name="chk" value="del">Enable Delete</input>"""),
                            ))
    message += """</td></tr></table>"""
    return message

def status():
    try:
        message  = ""
        stat = json.loads(open('/dev/shm/jukebox.json').read())
	if 'current' in stat:
            current = os.path.split(stat['current'])[1]
            message += 'Now Playing: <em>' + current + '</em><br/>'
            global title
            title = 'Jukebox - %s' % current
        length = stat.get('length', None)
	if length:
            message += str(length) + ' queued<br/><ol><li>'
            queue = stat.get('queue', [])
            message += '</li><li>'.join([x[0] + str(x[1]) for x in queue])
        message += '</li></ol>'
        return message
    except:
#        return '\n<!--\n' + traceback.format_exc() + '\n-->\n'
        return ''

files = fileList()

with open('/dev/shm/songs.csv','w') as w:
    c = csv.writer(w)
    c.writerow(('letter','number','name'))
    for l in sorted(files):
        for n in sorted(files[l]):
            c.writerow((l,n,files[l][n]))

message = '&nbsp'.join(['<a href="#letter_%s">%s</a>' %
                        (l, l) for l in sorted(files)])

message += '<br/>'

message += status()

message += buttons()

message += uploadFile(upload, letter, number)

message += process(submit, letter, number)

message += playlist(files)

message += uploader(files)

message += '<br/><a href="/jukebox/songs.csv">songs.csv</a><br/>'

print """\
Content-Type: text/html\n
<head><title>%s</title></head>
<html><body>
<p>%s</p>
</body></html>
""" % (title, message)
