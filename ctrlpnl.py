# Include code common to both, such as command/response code, serial code, baud rate, magic number, endianness, etc.
# This ensures that changes to the communication strategy will change both host and device code

import serial
import hashlib
import tkinter as tk
from tkinter import ttk
import json
import os

try:
    gpio_module = __import__("gpiozero")
    Button = getattr(gpio_module, "Button")
except ModuleNotFoundError:
    Button = None

import sys

import time

#import board
#import adafruit_pcf8591.pcf8591 as PCF
#from adafruit_pcf8591.analog_in import AnalogIn

BYTE_ORDER = 'big'

MAGIC_NUMBERS = 0x2271b6bb

DEFAULT_BAUD = 921600

HASH = hashlib.md5

COMMANDS = [
    "open",
    "remove_page",
    "add_script",
    "assign_script",
    "button_pressed",
    "dial_changed",
    "add_page",
    "send_function",
    "load_scripts",
    "update_color",
    "send_page",
    "remove_page",
    "next_page",
    "previous_page",
    "get_page",
    "send_value"
]

RESPONSES = ["ack", "nack", "bad hash", "bad magic values"]


# Identifier can be a command or a response code
def send(port, identifier, data):
    stream = MAGIC_NUMBERS.to_bytes(4, byteorder=BYTE_ORDER) + identifier.to_bytes(4, byteorder=BYTE_ORDER) \
             + data.__len__().to_bytes(4, byteorder=BYTE_ORDER) + data

    md = HASH()
    md.update(stream)

    stream += md.digest()

    port.write(stream)


def receive(port):
    magic = port.read(4)
    identifier = port.read(4)
    length = port.read(4)

    len = int.from_bytes(length, byteorder=BYTE_ORDER)

    data = port.read(len)

    digest = port.read(HASH().digest_size)

    message = magic + identifier + length + data

    md = HASH()
    md.update(message)

    identifier = int.from_bytes(identifier, byteorder=BYTE_ORDER)

    return {"identifier": identifier, "digest_valid": digest == md.digest(), "magic_valid": int.from_bytes(magic, byteorder=BYTE_ORDER) == MAGIC_NUMBERS, "data": data}


class Page:
    def __init__(self):
        pass


class CtrlPnlComs:
    def __init__(self, port, baud=DEFAULT_BAUD):
        self.serial = serial.Serial(port, baud)

    def __del__(self):
        self.serial.close()

    def inBufferSize(self):
        return self.serial.in_waiting

    def write(self, command, data=b''):
        # Send data
        send(self.serial, COMMANDS.index(command), data)

        # Wait for response
        response = receive(self.serial)

        return response

    def read(self):
        # Capture input message
        response = receive(self.serial)

        # Send acknowledge
        if response["magic_valid"] is False:
            ack = 3
        elif response["digest_valid"] is False:
            ack = 2
        else:
            ack = 0

        send(self.serial, ack, b'')

        return response

    def add_script(self, script_path):
        script_name = os.path.basename(script_path)
        data = script_name.__len__().to_bytes(4, byteorder=BYTE_ORDER)
        data += script_name.encode(encoding='UTF-8')
        with open(script_path, "rb") as file:
            data += file.read()
        return self.write("add_script", data)

    def send_function(self, script_name, function_name):

        data = script_name.__len__().to_bytes(4, byteorder=BYTE_ORDER)
        data += script_name.encode(encoding='UTF-8')
        data += function_name.__len__().to_bytes(4, byteorder=BYTE_ORDER)
        data += function_name.encode(encoding='UTF-8')

        response = self.write("send_function", data)

        colour_response = self.read()

        return json.loads(colour_response["data"].decode('UTF-8'))
    
    def send_value(self, script_name, value_name, value):
        
        data = script_name.__len__().to_bytes(4, byteorder=BYTE_ORDER)
        data += script_name.encode(encoding='UTF-8')
        
        data += value_name.__len__().to_bytes(4, byteorder=BYTE_ORDER)
        data += value_name.encode(encoding='UTF-8')
        
        data += value.to_bytes(4, byteorder=BYTE_ORDER)

        response = self.write("send_value", data)
        
        

    # Inform the host to initialise the list of scripts
    def load_scripts(self, scripts):

        data = b''

        print("len: " + str(len(scripts)))

        data += len(scripts).to_bytes(4, byteorder=BYTE_ORDER)

        for script in scripts:
            data += script.__len__().to_bytes(4, byteorder=BYTE_ORDER)
            data += script.encode(encoding='UTF-8')

        response = self.write("load_scripts", data)

        print(response)

