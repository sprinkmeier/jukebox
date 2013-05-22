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
import tarfile
import time
import traceback
import zipfile

LETTERS = "ABCDEFGHJKLMNPQRSTUV"

PORT    = 55555
ADDRESS = ('localhost', PORT)

CONFIG = '/var/jukebox/config.json'

cgitb.enable()

title = 'Jukebox'

config = {
    'dup': False,
    'rpt': False,
    'rnd': False,
    'lim': 0,
    }
try:
    conf = json.loads(open(CONFIG).read())
    for k,v in config.items():
        config[k] = type(v)(conf[k])
except:
    pass

form = cgi.FieldStorage()
number = form.getvalue('number', None)
letter = form.getvalue('letter', None)
submit = form.getvalue('submit', None)
chk    = form.getvalue('chk', [])
limit  = form.getvalue('limit', 0)

try:
    upload = form['file']
except:
    upload = None

def sanitize_filename(fname):
    sane = set(string.letters + string.digits + '-_.')
    return ''.join(c for c in fname if c in sane)

def tr(d):
    if not d:
        return '<tr/>\n'
    return '<tr><td>' + '</td><td>'.join(d) + '</td></tr>\n'

def ip(typ, name, val, html = None):
    ret =  '''<input type="{typ}" name="{name}" value="{val}"'''.format(typ=typ, name=name, val=val)
    if not html:
        return ret+'/>'
    return ret + '>' + html + '</input>'

def btn(val):
    return ip('submit', 'submit', val)

def hide(name, val):
    return ip('hidden', name, val)

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
    if submit == "Set":
        global config
        config = {
            'dup': 'dup' in chk,
            'rpt': 'rpt' in chk,
            'rnd': 'rnd' in chk,
            'lim': int(limit),
            }
        with open(CONFIG,'w') as w:
            w.write(json.dumps(config, indent=4, sort_keys=1))
            w.write('\n')
        return ''
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
    if 'del' in chk:
        delBtn = btn('Delete')
    else:
        delBtn = ''

    playBtn = btn('Play')
    message = '<table border="1">\n'

#    URL_FMT = "http://%s:%s/%s?letter=%%s&number=%%d" % (
#        os.environ['SERVER_NAME'],
#        os.environ['SERVER_PORT'],
#        os.environ['SCRIPT_NAME'])
#    message += "<!-- %s -->\n" % URL_FMT

    BTNS_FMT = """<form action="%s" method="post">
    %s %s %s %s
</form>""" %  (os.environ['SCRIPT_NAME'],
               hide('letter', '{letter}'),
               hide('number', '{number}'),
               playBtn, delBtn)

    for letter in sorted(files):
        d = files[letter]
        col1 = '<td rowspan="%d" id="letter_%s">%s</td>' % (len(d), letter, button(letter))

        for number in sorted(d):
            esc = '/jukebox/%s/%d/%s' % (letter, number, d[number])
            esc = esc.replace("'", "&#054;")
            name = "<a href='%s'>%s</a>" % (esc, d[number])
            message += ("""\
<TR>
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

def options(opts, selected):
    ret = ''
    for (val, name) in opts:
        if (val ==selected):
            ret += '<option value="%s" selected>%s</option>\n' % (val, name)
        else:
            ret += '<option value="%s">%s</option>\n' % (val, name)
    return ret

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
        <p>%s</p>
    </form>
""" % (os.environ['SCRIPT_NAME'], letters, numbers, btn('Upload'))


    return message

def button(name, extra = ""):
    return """
   <form enctype="multipart/form-data" action="%s" method="post">
        <input type="submit" name="submit" value="%s">
        %s
    </form>
""" % (os.environ['SCRIPT_NAME'], name, extra)


def buttons():
    message  = "<table>"
    message += tr((button("Stop"),
                   button("Flush"),
                   button("Shutdown"),
                   button("Download"),
                   button("Refresh","""<input type="checkbox" name="chk" value="del">Enable Delete</input>"""),
                            ))
    message += "</table>"
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
            message += str(length) + ' queued<br/>'
            queue = stat.get('queue', [])
            message += '<table>'
            while queue:
                message += tr([x[0] + str(x[1]) for x in queue[:16]])
                queue = queue[16:]
            message += '</table>'
        return message
    except:
#        return '\n<!--\n' + traceback.format_exc() + '\n-->\n'
        return ''

def checkbox(val, name, checked = False):
    checked = (" checked", "")[not checked]
    return '<input type="checkbox" name="chk" value="%s"%s>%s</input>' % (val, checked, name)

def conf_options():
    return """\
<center><FORM ACTION="{cgi}" METHOD="POST">
{dup}{rpt}{rnd}
&nbsp;&nbsp;&nbsp;&nbsp;
Queue Limit: <SELECT NAME="limit" SIZE=0>{opts}</SELECT>
<br/>
{btn}
</FORM></center>
""".format(cgi=os.environ['SCRIPT_NAME'],
           btn=btn('Set'),
           conf = repr(config),
           chk = repr(chk),
           lim = repr(limit),
           dup = checkbox('dup','Allow Duplicates', config['dup']),
           rpt = checkbox('rpt', 'Repeat',          config['rpt']),
           rnd = checkbox('rnd', 'Random',          config['rnd']),
           opts = options((( 0, 'unlimited'),
                           ( 1, 1), ( 2, 2),
                           ( 3, 3), ( 5, 5),
                           (10,10), (15,15),
                           (20,20), (50,50),
                           ),
                          config['lim']),
           )

files = fileList()

if (submit == "Download"):
    if 1: # ZIP don't work.
        if 1: # gz is overkill
            print("""Content-Type: application/tar
Content-Disposition: attachment; filename="songs.tar"
""")
            t = tarfile.open('songs.tar', 'w|', sys.stdout)
        else:
            print("""Content-Type: application/x-gzip
Content-Disposition: attachment; filename="songs.tar.gz"
""")
            t = tarfile.open('songs.tar.gz', 'w|gz', sys.stdout)
        t.add('/dev/shm/songs.csv','songs.csv')
        for l in sorted(files):
            for n in sorted(files[l]):
                fn = files[l][n]
                t.add('/var/jukebox/%s/%d/%s' % (l,n,fn),
                      '%s%d - %s' % (l,n,fn))
        t.close()
    else:
        # .zip files have better legacy support
        # BUT!!!
        # the zipfile lib does not seem to support stream output.
        # makes sense, zipfiles have an index at the end of the file,
        # so seeking is assumed.
        print("""Content-Type: application/zip
Content-Disposition: attachment; filename="songs.zip"
""")
        z = zipfile.ZipFile(sys.stdout,'w',compression=zipfile.ZIP_DEFLATED)
        for l in sorted(files):
            for n in sorted(files[l]):
                fn = files[l][n]
                z.write('/var/jukebox/%s/%d/%s' % (l,n,fn),
                        '%s%d - %s' % (l,n,fn))
        z.close()

    sys.exit(0)


with open('/dev/shm/songs.csv','w') as w:
    c = csv.writer(w)
    c.writerow(('letter','number','name'))
    for l in sorted(files):
        for n in sorted(files[l]):
            c.writerow((l,n,files[l][n]))

message = '&nbsp'.join(['<a href="#letter_%s">%s</a>' %
                        (l, l) for l in sorted(files)])

message += '<br/>\n<!-- '+repr((number, letter, submit, chk))+' -->\n'

message += status()

message += buttons()

message += uploadFile(upload, letter, number)

message += process(submit, letter, number)

message += playlist(files)

message += uploader(files)

message += '<br/><a href="/jukebox/songs.csv">songs.csv</a><br/>'

message += conf_options()

print """\
Content-Type: text/html\n
<head><title>%s</title></head>
<html><body>
<p>%s</p>
</body></html>
""" % (title, message)
