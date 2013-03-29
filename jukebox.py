#!/usr/bin/env python

import glob
import json
import os
import select
import serial
import socket
import subprocess
import sys
import time
import traceback



SERIAL  = (glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + [''])[0]
PORT    = 55555

LETTERS = "ABCDEFGHJKLMNPQRSTUV"
NUMBERS = range(1,9)

DevNull = open('/dev/null','rw')

try:
    ser = serial.Serial(SERIAL)
    ser.setBaudrate(9600)
except:
    ser = None
    traceback.print_exc()

Q = []

p = None
filename = None

def play(filename):
    p = subprocess.Popen(('play', filename),
                         stdout = DevNull,
                         stdin  = DevNull,
                         stderr = DevNull)

    return p

def playGlob(filenameGlob):
    filenames = glob.glob(filenameGlob)
    if (len(filenames) == 1):
        filename = filenames[0]
        return (filename, play(filename))
    return None

class AtomicFile(object):
    def __init__(self, filename, mode = 'w'):
        self.filename = filename
        self.new = filename + ".new"
        self.w = open(self.new, mode)

    def __enter__(self, *extra):
        #print(extra)
        return self.w

    def __exit__(self, *extra):
        #print(extra)
        self.w.close()
        os.rename(self.new, self.filename)

def process(data, address):
    global p
    global Q


    if not data: return

    print(data, address)

    if (data == 'Stop'):
        if p:
            p.kill()
        return

    if (data == 'Flush'):
        Q = []
        return

    if (data == 'Shutdown'):
        os.system("sudo /sbin/shutdown")
        return

    if (data == 'Play'):
        return
    try:
        data = data.split()
        if (len(data) != 2): return
        (letter, number) = data
        assert(letter in LETTERS)
        number = int(number)
        assert(number in NUMBERS)
        Q.append((letter, number, time.time(), address))
    except:
        traceback.print_exc()

def dump(data):
    with AtomicFile('/dev/shm/jukebox.json') as w:
        w.write(json.dumps(data, indent=4, sort_keys=1))


# Create a UDP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
sock.bind(('0.0.0.0', PORT))

if ser:
    rs = (sock, ser)
else:
    rs = (sock,)

while True:
    (r,w,x) = select.select(rs,(),(),1)

    try:
        if sock in r:
            (data, address) = sock.recvfrom(4096)
            process(data, address)
        elif ser in r:
            try:
                data = ser.readline().strip()
            except:
                rs = (sock,)
            process(data, SERIAL)
    except:
        pass

    if p:
        if p.poll() is not None:
            print(p.wait())
            p = None
            filename = None
        else:
            print(filename)
    if Q:
        if p:
            print(Q)
        else:
            (letter, number, epoch, address) = Q.pop(0)
            p = playGlob("/var/jukebox/%s/%d/*" % (letter, number))
            if p:
                (filename, p) = p
    elif p:
        print(filename)
    else:
        print('.')

    dump({'current': filename,
          'length' : len(Q),
          'queue'  : Q,
          })
