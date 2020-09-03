# Include code common to both, such as command/response code, serial code, baud rate, magic number, endianness, etc.
# This ensures that changes to the communication strategy will change both host and device code

import serial
import hashlib
import tkinter as tk
import json
import os

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
    "update_color"
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

    data = port.read(int.from_bytes(length, byteorder=BYTE_ORDER))

    digest = port.read(HASH().digest_size)

    message = magic + identifier + length + data

    md = HASH()
    md.update(message)

    identifier = int.from_bytes(identifier, byteorder=BYTE_ORDER)

    return {"identifier": identifier, "digest_valid": digest == md.digest(), "magic_valid": int.from_bytes(magic, byteorder=BYTE_ORDER) == MAGIC_NUMBERS, "data": data}


class Page:
    def __init__(self):
        pass


class CtrlPnl:
    def __init__(self, port, baud=DEFAULT_BAUD):
        self.serial = serial.Serial(port, baud)

    def __del__(self):
        self.serial.close()

    def inBufferSize(self):
        return self.serial.in_waiting

    def write(self, command, data):
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


class PanelButton(tk.Frame):
    def __init__(self, ctrlpnl, master=None):
        super(PanelButton, self).__init__(master)
        self.master = master
        self.pack()

        self.label = tk.Label(self)
        self.label.pack(side="top")
        self.label["text"] = ""

        self.button = tk.Button(self)
        self.button.pack(side="top")
        self.button["text"] = "    "

        self.indicator = tk.Label(self)
        self.indicator["text"] = " "
        self.indicator.pack(side="top")
        self.indicator["bg"] = "red"

        self.script_name = ""
        self.function_name = ""

        self.ctrl = ctrlpnl

    def text(self, str):
        self.label["text"] = str

    def background(self, color):
        self.indicator["bg"] = color

    def enabled(self, isEnabled):
        self.button["state"] = "normal" if isEnabled == True else "disable"

    def send_function(self):
        cols = self.ctrl.send_function(self.script_name, self.function_name)
        print("Cols: " + str(cols))
        self.master.master.colours(cols)

    def set_function(self, script, function):
        self.script_name = script
        self.function_name = function
        self.button["command"] = self.send_function


class PanelRow(tk.Frame):
    def __init__(self, widget, ctrlpnl, master=None):
        super(PanelRow, self).__init__(master)

        self.widget_list = []
        self.pack()

        for i in range(4):
            self.widget_list.append(widget(ctrlpnl, self))
            self.widget_list[i].pack(side="left")


class CtrlPnlFrame(tk.Frame):

    def __init__(self, ctrlpnl, master=None):
        super(CtrlPnlFrame, self).__init__(master)

        self.master = master
        self.pack()

        self.row1 = PanelRow(PanelButton, ctrlpnl, self)
        self.row2 = PanelRow(PanelButton, ctrlpnl, self)

        self.widget_list = self.row1.widget_list + self.row2.widget_list

    def colours(self, colours):
        for key in colours.keys():
            for widget in self.widget_list:
                if key == widget.function_name:
                    widget.background(colours[key])
