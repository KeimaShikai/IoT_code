#!/usr/bin/python3
import os
import sys

if not os.getegid() == 0:
    sys.exit('Script must be run as root')

from time import sleep
from pyA20.gpio import gpio
from pyA20.gpio import port

led = port.PA6

gpio.init()
gpio.setcfg(led, gpio.OUTPUT)

try:
    print ("Press CTRL+C to exit")
    while True:
        gpio.output(led, 1)
        sleep(0.1)
        gpio.output(led, 0)
        sleep(0.1)

        gpio.output(led, 1)
        sleep(0.1)
        gpio.output(led, 0)
        sleep(0.1)

        sleep(0.6)
except KeyboardInterrupt:
    print ("Goodbye.")
