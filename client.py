#! /usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import lcd_i2c as lcd
import os
import sys
import glob
import logging
import logging.handlers
import time

if not os.getegid() == 0:
    sys.exit('Script must be run as root')

#from time import sleep
from pyA20.gpio import gpio
from pyA20.gpio import port
from os.path import dirname, abspath

WORK_DIR = dirname(abspath(__file__))

led = port.PA6

gpio.init()
gpio.setcfg(led, gpio.OUTPUT)

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
#bus = smbus.SMBus(1) # Rev 2 Pi uses 1

LOG_FILENAME = WORK_DIR + '/log'

# Set up a specific logger with our desired output level
my_logger = logging.getLogger('IoT_Logger')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=5*1024*1024, backupCount=2)

my_logger.addHandler(handler)

sock = socket.socket()
sock.bind(('', 8888))
sock.listen(2)
#lcd.lcd_init()
#lcd.lcd_string("Ah, shit",LCD_LINE_1)
#lcd.lcd_string("Here we go again",LCD_LINE_2)

def get_data(connection):
    data = connection.recv(1024).decode().strip()
    print(data)
    return data

def log_write(data):
    for message in data:
        my_logger.debug(message + '\n')

while True:
    if (sock.accept()):
        break
    else:
        lcd.lcd_init()
        lcd.lcd_string("Ah, shit",LCD_LINE_1)
        lcd.lcd_string("Here we go again",LCD_LINE_2)
        time.sleep(2)

while True:
    conn, addr = sock.accept()
    print('connected:', addr)
    data = get_data(conn)
    temperature_str = data[11:20]
    humidity_str = data[22:31]
    temperature_float = float(temperature_str[4:9])
    humidity_float = float(humidity_str[4:9])
    if (temperature_float > 30):
        gpio.output(led, 1)
    elif (humidity_float > 55):
        gpio.output(led, 1)
    else:
        gpio.output(led, 0)
    log_write([data])
    conn.close()
    print('diconnected:', addr)
    lcd.lcd_init()
    lcd.lcd_string(temperature_str, LCD_LINE_1)
    lcd.lcd_string(humidity_str, LCD_LINE_2)
