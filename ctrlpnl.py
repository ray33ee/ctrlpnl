# Include code common to both, such as command/response code, serial code, baud rate, magic number, endianness, etc.
# This ensures that changes to the communication strategy will change both host and device code

import serial
import hashlib
import tkinter as tk
from tkinter import ttk
import json
import os
from gpiozero import Button

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
    "get_page"
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

    def clear(self):
        self.text("")
        self.button["command"] = None
        self.background("white")
        self.script_name = ""
        self.function_name = ""
        
    def click(self):
        if self.button["state"] == "normal":
            self.send_function()




class PanelCombos(tk.Frame):
    def __init__(self, scripts_and_functions, master=None):
        super(PanelCombos, self).__init__(master)
        self.master = master
        self.pack()

        self.script = ttk.Combobox(self)
        self.script.pack(side="top")
        self.script["state"] = "readonly"

        self.function = ttk.Combobox(self)
        self.function.pack(side="top")
        self.function["state"] = "readonly"

        self.scripts_and_functions = scripts_and_functions

        self.script.bind("<<ComboboxSelected>>", self.selected_handler)

    def set_script(self, script, function):
        self.script.current(list(self.scripts_and_functions.keys()).index(script))
        self.function["values"] = self.scripts_and_functions[script]["functions"]
        self.function.current(self.scripts_and_functions[script]["functions"].index(function))

    def selected_handler(self, event):
        self.function["values"] = self.scripts_and_functions[self.script.get()]["functions"]
        self.function.current(0)





class PanelRow(tk.Frame):
    def __init__(self, widget, ctrlpnl=None, s_and_f=None, master=None):
        super(PanelRow, self).__init__(master)

        self.widget_list = []
        self.pack()

        for i in range(4):
            if not ctrlpnl:
                self.widget_list.append(widget(s_and_f, self))
            else:
                self.widget_list.append(widget(ctrlpnl, self))
            self.widget_list[i].pack(side="left")


class PageNavigator(tk.Frame):
    def __init__(self, master=None):
        super(PageNavigator, self).__init__(master)

        self.pack(fill="x")

        self.left_button = tk.Button(self)
        self.left_button.pack(side="left")

        self.right_button = tk.Button(self)
        self.right_button.pack(side="right")

        self.title = tk.Label(self)
        self.title.pack()




class CtrlPnlFrame(tk.Frame):

    def __init__(self, port, config_path, master=None):
        super(CtrlPnlFrame, self).__init__(master)

        self.master = master
        self.pack()

        self.pnl = CtrlPnl(port)

        self.row1 = PanelRow(PanelButton, self.pnl, None, self)
        self.row2 = PanelRow(PanelButton, self.pnl, None, self)

        self.navigator = PageNavigator(self)
        self.navigator.pack(side="bottom")

        self.navigator.left_button["command"] = self.previous
        self.navigator.right_button["command"] = self.next

        self.widget_list = self.row1.widget_list + self.row2.widget_list

        self.script_dictionary = {}

        self.config = {}

        self.page_index = 0

        self.scripts_dir = "./scripts/"

        with open("device_config.json", "r") as infile:
            self.config = json.load(infile)

        print(json.dumps(self.config))

        self.loadPage()

        self.get_page()
        
        self.pins = ["J8:11", "J8:13"]
        
        self.hardware_buttons = []
        
        self.prev_button_state = []
        
        for i in range(len(self.pins)):
            self.hardware_buttons.append(Button(self.pins[i]))
            self.prev_button_state.append(False)
            #self.hardware_buttons[i].when_pressed = self.widget_list[i].click
        

    def next(self):
        self.page_index += 1

        if self.page_index == len(self.config["pages"]):
            self.page_index = len(self.config["pages"]) - 1

        print(self.page_index)

        self.loadPage()

        self.get_page()

    def previous(self):
        self.page_index -= 1

        if self.page_index == -1:
            self.page_index = 0

        self.loadPage()

        self.get_page()

    def get_page(self):
        self.pnl.write("get_page", json.dumps(self.config["pages"][self.page_index]).encode('UTF-8'))

    def update(self):
        super(CtrlPnlFrame, self).update()
        
        for i in range(len(self.hardware_buttons)):
            if self.prev_button_state[i] == False and self.hardware_buttons[i].is_pressed == True:
                self.widget_list[i].click()
            self.prev_button_state[i] = self.hardware_buttons[i].is_pressed
            
        

        if self.pnl.inBufferSize() != 0:
            response = self.pnl.read()
            command_string = COMMANDS[response["identifier"]]
            data = response["data"]

            if command_string == "open":
                pass
            elif command_string == "add_script":
                length = int.from_bytes(data[0:4], byteorder=BYTE_ORDER)
                title = data[4:length + 4].decode(encoding='UTF-8')
                script = data[length + 4:]
                with open(title, "wb") as fp:
                    fp.write(script)
            elif command_string == "assign_script":
                pass
            elif command_string == "button_pressed":
                pass
            elif command_string == "dial_changed":
                pass
            elif command_string == "add_page":
                entry = {
                    "title": "",
                    "scripts": [],
                    "buttons": [
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {}
                    ],
                    "dials": ["", "", "", ""]
                }

                self.config["pages"].insert(self.page_index + 1, entry)

                with open("device_config.json", "w") as outfile:
                    json.dump(self.config, outfile, indent=4)
            elif command_string == "send_page":
                page = json.loads(data.decode('UTF-8'))

                self.config["pages"][self.page_index] = page

                with open("device_config.json", "w") as outfile:
                    json.dump(self.config, outfile, indent=4)

                self.loadPage()

            elif command_string == "update_color":
                pass
            elif command_string == "remove_page":
                self.config["pages"].pop(self.page_index)

                with open("device_config.json", "w") as outfile:
                    json.dump(self.config, outfile, indent=4)

                if self.page_index == len(self.config["pages"]):
                    self.page_index = len(self.config["pages"])-1

                self.loadPage()
            elif command_string == "next_page":
                self.next()
            elif command_string == "previous_page":
                self.previous()
            elif command_string == "get_page":
                self.get_page()

            print("command: " + command_string)
            print(response)


    def clear(self):
        for widget in self.widget_list:
            widget.clear()

    def loadPage(self):
        page = self.config["pages"][self.page_index]
        scripts = set()
        buttons = page["buttons"]

        for button in buttons:
            if len(button) != 0:
                scripts.add(button["script"])

        self.clear()

        self.navigator.title["text"] = page["title"]

        self.script_dictionary.clear()

        print("Scripts: " + str(scripts))

        for i in range(8):
            if len(buttons[i]) != 0:
                print("Nth Script: " + buttons[i]["script"])
                print("Nth Function: " + buttons[i]["function"])
                self.widget_list[i].text(buttons[i]["name"])
                self.widget_list[i].set_function(buttons[i]["script"], buttons[i]["function"])
                self.widget_list[i].enabled(True)
            else:
                self.widget_list[i].enabled(False)
                self.widget_list[i].text("")

        if len(scripts) != 0:
            self.pnl.load_scripts(scripts)

            for _ in scripts:
                colour_response = self.pnl.read()

                print("COlours: " + str(colour_response))

                self.colours(json.loads(colour_response["data"].decode('UTF-8')))

    def colours(self, colours):
        if colours:
            for key in colours.keys():
                for widget in self.widget_list:
                    if key == widget.function_name:
                        widget.background(colours[key])
