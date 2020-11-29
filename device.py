from ctrlpnl import CtrlPnlComs, COMMANDS, BYTE_ORDER

import tkinter as tk
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


class PanelButton(tk.Frame):
    def __init__(self, ctrlpnl, master=None):
        super(PanelButton, self).__init__(master)
        self.master = master
        # self.pack()

        self.label = tk.Label(self)
        self.label.grid(row=0, column=0, sticky="NSEW")
        self.label["text"] = ""

        self.button = tk.Button(self)
        self.button.grid(row=1, column=0, sticky="NSEW")
        self.button["text"] = "    "

        self.indicator = tk.Label(self)
        self.indicator["text"] = " "
        self.indicator.grid(row=2, column=0, sticky="NSEW")
        self.indicator["bg"] = "red"

        self.script_name = ""
        self.function_name = ""

        self.ctrl = ctrlpnl

        self.grid_rowconfigure(0, weight=20)
        self.grid_rowconfigure(1, weight=100)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def text(self, str):
        self.label["text"] = str

    def background(self, color):
        self.indicator["bg"] = color

    def enabled(self, isEnabled):
        self.button["state"] = "normal" if isEnabled == True else "disable"

    def send_function(self):
        cols = self.ctrl.send_function(self.script_name, self.function_name)
        print("Cols: " + str(cols))
        self.master.colours(cols, self.script_name)

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


class CtrlPnlDeviceFrame(tk.Frame):

    def __init__(self, port, config_path, master=None):
        super(CtrlPnlDeviceFrame, self).__init__(master)

        self.master = master
        self.pack(fill=tk.BOTH, expand=1)

        self.pnl = CtrlPnlComs(port)

        self.widget_list = []

        for j in range(2):
            for i in range(4):
                self.widget_list.append(PanelButton(self.pnl, self))
                # self.widget_list[i+j*4].pack(side="left")
                self.widget_list[i + j * 4].grid(row=j, column=i, sticky="NSEW")

        self.left_button = tk.Button(self)
        self.left_button.grid(row=2, column=0, sticky="NSEW")

        self.title = tk.Label(self)
        self.title.grid(row=2, column=1, sticky="NSEW")

        self.right_button = tk.Button(self)
        self.right_button.grid(row=2, column=3, sticky="NSEW")

        # self.navigator = PageNavigator(self)
        # self.navigator.pack(side="bottom")
        # self.navigator.grid(row=2, column=0, sticky="NSEW")

        self.quitter = tk.Button(self)
        self.quitter.grid(row=2, column=2, sticky="NSEW")
        self.quitter["command"] = master.destroy

        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.left_button["command"] = self.previous
        self.right_button["command"] = self.next

        self.script_dictionary = {}

        self.config = {}

        self.page_index = 0

        self.scripts_dir = "./scripts/"

        with open("device_config.json", "r") as infile:
            self.config = json.load(infile)

        print(json.dumps(self.config))

        self.loadPage()

        self.get_page()
        
		#self.pins = ["J8:36", "J8:38", "J8:40", "J8:15", "J8:11", "J8:13", "J8:16", "J8:7"]
        self.pins = ["J8:7", "J8:16", "J8:13", "J8:11", "J8:15", "J8:40", "J8:38", "J8:36"]

        self.hardware_buttons = []

        self.prev_button_state = []

        if Button:
            for i in range(len(self.pins)):
                self.hardware_buttons.append(Button(self.pins[i]))
                self.prev_button_state.append(False)
                # self.hardware_buttons[i].when_pressed = self.widget_list[i].click

        # pcf = PCF.PCF8591(board.I2C())

        # self.dial_0 = AnalogIn(pcf, PCF.A0)

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
        super(CtrlPnlDeviceFrame, self).update()

        for i in range(len(self.hardware_buttons)):
            if self.prev_button_state[i] == False and self.hardware_buttons[i].is_pressed == True:
                self.widget_list[i].click()
            self.prev_button_state[i] = self.hardware_buttons[i].is_pressed

        # self.dial_0.value

        # self.pnl.send_value("volume_script", "volume", self.dial_0.value)

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

        self.title["text"] = page["title"]

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

            for script in scripts:
                colour_response = self.pnl.read()

                print("COlours: " + str(colour_response))


                self.colours(json.loads(colour_response["data"].decode('UTF-8')), script)


    def colours(self, colours, script_name):
        if colours:
            for key in colours.keys():
                for widget in self.widget_list:
                    if key == widget.function_name and script_name == widget.script_name:
                        widget.background(colours[key])


# Make sure host and device do not send commands at the same time

root = tk.Tk()
#root.attributes('-fullscreen', True)

app = CtrlPnlDeviceFrame("/dev/ttyS0", "device_config.json", master=root)


while True:
    app.update_idletasks()
    app.update()




