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
lcd.lcd_init()
lcd.lcd_string("Ah, shit",LCD_LINE_1)
lcd.lcd_string("Here we go again",LCD_LINE_2)

class device(object):

    def __init__(self, number, temperature, humidity):
        self.t_range = [25.0, 25.0, 25.0, 25.0, 25.0]
        self.h_range = [28.0, 28.0, 28.0, 28.0, 28.0]
        self.number = number
        self.t_range[0] = temperature
        self.t_range[0] = humidity
        self.t_avg = sum(self.t_range) / len(self.t_range)
        self.h_avg = sum(self.h_range) / len(self.h_range)
        self.curr_indication = 1

    def update(self, temperature, humidity):
        self.t_range[self.curr_indication] = temperature
        self.h_range[self.curr_indication] = humidity
        if (self.curr_indication == 4):
            self.curr_indication = 0
        else:
            self.curr_indication += 1
        self.t_avg = sum(self.t_range) / len(self.t_range)
        self.h_avg = sum(self.h_range) / len(self.h_range)       

def get_data(connection):
    data = connection.recv(1024).decode().strip()
    print(data)
    return data

def log_write(data):
    for message in data:
        my_logger.debug(message + '\n')

def parser(data): #TODO remove t_str, h_str
    number = int(data[8:9])
    t_str = data[11:20]
    h_str = data[22:31]
    t_float = float(t_str[4:9])
    h_float = float(h_str[4:9])
    return number, t_float, h_float

def led_checker(average_temp, average_humid):
    if ((average_temp < 20) or (average_temp > 30)):
        gpio.output(led, 1)
    elif ((average_humid < 20) or (average_humid > 55)):
        gpio.output(led, 1)
    else:
        gpio.output(led, 0)

'''
while True:
    conn, addr = sock.accept()
    if (): #TODO check for the connection
        conn.close()
        break
    else:
        lcd.lcd_init()
        lcd.lcd_string("Ah, shit",LCD_LINE_1)
        lcd.lcd_string("Here we go again",LCD_LINE_2)
        time.sleep(2)
'''

#Current data example:
#Sensor #1. T = 25.80; H = 26.40
devices = []

while True:
    isNew = True
    conn, addr = sock.accept()
    print('connected:', addr)
    data = get_data(conn)
    number, temperature_float, humidity_float = parser(data)
    
    for each in devices:
        if (each.number == number):
            isNew = False
            each.update(temperature_float, humidity_float)

    if (isNew):
        new = device(number, temperature_float, humidity_float)
        devices.append(new)

    log_write([data])
    conn.close()
    print('diconnected:', addr)

    average_temp = average_humid = 0
    for each in devices:
        average_temp += each.t_avg
        average_humid += each.h_avg
    average_temp = round(average_temp / len(devices), 2)
    average_humid = round(average_humid / len(devices), 2)
    
    led_checker(average_temp, average_humid)
    
    lcd.lcd_init()
    lcd.lcd_string("T = " + str(average_temp), LCD_LINE_1)
    lcd.lcd_string("H = " + str(average_humid), LCD_LINE_2)
    
    time.sleep(3)
