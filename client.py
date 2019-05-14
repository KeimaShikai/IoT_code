#! /usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import lcd_i2c as lcd

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

sock = socket.socket()
sock.bind(('', 8888))
sock.listen(2)
lcd.lcd_init()
lcd.lcd_string("Ah, shit",LCD_LINE_1)
lcd.lcd_string("Here we go again",LCD_LINE_2)

def get_data(connection):
    data = connection.recv(1024).decode().strip()
    print(data)
    return data

while True:
    with open('log.txt', 'a') as file:
        conn, addr = sock.accept()
        print('connected:', addr)
        data = get_data(conn)
        temperature = data[11:20]
        humidity = data[22:31]
        file.write(data + '\n')
        conn.close()
        print('diconnected:', addr)
        lcd.lcd_string(temperature, LCD_LINE_1)
        lcd.lcd_string(humidity, LCD_LINE_2)
