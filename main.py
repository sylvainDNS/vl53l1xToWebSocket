#!/usr/bin/env python

import signal

import os
import time
from datetime import datetime

import json
import uuid

from socketIO_client import SocketIO, BaseNamespace


import VL53L1X

WS_HOST = os.getenv('WS_HOST', 'localhost')
WS_PORT = os.getenv('WS_PORT', 4444)
POOP_LOCATION = os.getenv('POOP_LOCATION', 'NC')

print("""

Press Ctrl+C to exit.

""")

tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open() 
tof.start_ranging(1) 

running = True

def exit_handler(signal, frame):
    global running
    running = False
    tof.stop_ranging() # Stop ranging
    sys.stdout.write("\n")
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

class PoopNamespace(BaseNamespace):
    def on_chiotte_response(self, *args):
        print('on_chiotte_response', args)

socketIO = SocketIO(WS_HOST, WS_PORT)
poopNamespace = socketIO.define(PoopNamespace, '/poop')

while running:
    distance_in_mm = 0
    if(tof.get_distance() != distance_in_mm):
        distance_in_mm = tof.get_distance()
        data = json.dumps(
            {
                'id': str(uuid.uuid4()),
                'location': POOP_LOCATION,
                'timestamp': datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"),
                'pq': distance_in_mm
            }
        )
        print(data)
        poopNamespace.emit(data)
    time.sleep(0.5)

