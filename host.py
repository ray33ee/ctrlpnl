from datetime import datetime

from ctrlpnl import CtrlPnlComs, COMMANDS, BYTE_ORDER
import json
import tkinter as tk
import os
from tkinter import ttk
import pystray

from PIL import Image, ImageDraw, ImageColor
from pystray import MenuItem as item
from pystray import Menu

import threading

from time import sleep

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


class CtrlPnlHostFrame(tk.Frame):

    def __init__(self, master=None):
        super(CtrlPnlHostFrame, self).__init__(master)

        self.master = master

        self.buttons = tk.Frame(master)
        self.buttons.pack()

        self.new_page = tk.Button(self.buttons)
        self.new_page["text"] = "new page"
        self.new_page.pack(side="left")
        self.new_page["command"] = self.new_page_command

        self.remove_page = tk.Button(self.buttons)
        self.remove_page["text"] = "remove page"
        self.remove_page.pack(side="left")
        self.remove_page["command"] = self.remove_page_command

        self.send_page = tk.Button(self.buttons)
        self.send_page["text"] = "send page"
        self.send_page.pack(side="left")
        self.send_page["command"] = self.send_page_command

        self.next_page = tk.Button(self.buttons)
        self.next_page["text"] = "next page"
        self.next_page.pack(side="left")
        self.next_page["command"] = self.next_page_command

        self.previous_page = tk.Button(self.buttons)
        self.previous_page["text"] = "previous page"
        self.previous_page.pack(side="left")
        self.previous_page["command"] = self.previous_page_command

        self.get_page = tk.Button(self.buttons)
        self.get_page["text"] = "get page"
        self.get_page.pack(side="left")
        self.get_page["command"] = self.get_page_command

        self.page_name = tk.Entry(master)
        self.page_name.pack(side="top")

        self.label1 = tk.Label(master)
        self.label1["text"] = ""
        self.label1.pack(side="top")

        self.row1 = PanelRow(PanelCombos, None, master)
        self.row1.pack(side="top")

        self.label2 = tk.Label(master)
        self.label2["text"] = ""
        self.label2.pack(side="top")

        self.scripts_and_functions = {}

        self.row2 = PanelRow(PanelCombos, None, self.scripts_and_functions, master)
        self.row2.pack(side="top")

        self.combos = [*self.row1.widget_list, *self.row2.widget_list]

        i = 0
        for combo in self.combos:
            combo.script.set(str(i))
            i += 1

    def new_page_command(self):
        pnl.write("add_page")
        pnl.write("next_page")


    def remove_page_command(self):
        print("iojoijoij")
        pnl.write("remove_page", b'')
        self.load_combos()
        pnl.write("previous_page")

    def next_page_command(self):
        pnl.write("next_page")


    def previous_page_command(self):
        pnl.write("previous_page")


    def get_page_command(self):
        pnl.write("get_page")

    def send_page_command(self):

        buttons = []

        for combo in self.combos:
            button = {}
            if combo.script.get() != "":
                button["script"] = combo.script.get()
                button["function"] = combo.function.get()
                index = self.scripts_and_functions[combo.script.get()]["functions"].index(combo.function.get())
                button["name"] = self.scripts_and_functions[combo.script.get()]["names"][index]

            buttons.append(button)

        print(buttons)

        page = {
            "title": self.page_name.get(),
            "buttons": buttons,
            "dials": [
                "",
                "",
                "",
                ""
            ]
        }

        pnl.write("send_page", json.dumps(page).encode('UTF-8'))

    def load_names(self):
        self.scripts_and_functions = {
            "":
                {
                    "functions": [""],
                    "names": [""]
                }
        }
        ls = os.listdir(os.getcwd())
        for dir in ls:
            if dir[-10:] == "_script.py":
                script_name = dir[:-3]
                module = __import__(script_name)
                functions = getattr(module, "Script").functions()
                names = getattr(module, "Script").names()
                self.scripts_and_functions[script_name] = {"functions": functions, "names": names}

        for combo in self.combos:
            combo.scripts_and_functions = self.scripts_and_functions
        print(self.scripts_and_functions)

    def load_combos(self, dat):
        page = json.loads(dat.decode('UTF-8'))

        index = 0
        self.page_name.delete(0, tk.END)
        self.page_name.insert(0, page["title"])
        for button in page["buttons"]:
            self.combos[index].script["values"] = list(self.scripts_and_functions.keys())

            if len(button) != 0:
                self.combos[index].set_script(button["script"], button["function"])
            else:
                self.combos[index].set_script("", "")

            index += 1

def tick():
    if pnl.inBufferSize() != 0:
        response = pnl.read()
        command_string = COMMANDS[response["identifier"]]
        data = response["data"]

        if command_string == "send_function":
            script_len = int.from_bytes(data[0:4], byteorder=BYTE_ORDER)
            script_name = data[4:script_len + 4].decode('UTF-8')
            function_len = int.from_bytes(data[script_len + 4:script_len + 8], byteorder=BYTE_ORDER)
            function_name = data[script_len + 8:script_len + 8 + function_len + 8].decode('UTF-8')

            print("Script :" + script_name)
            print("Function :" + function_name)

            colours = script_dictionary[script_name].dictionary()["buttons"][function_name]["function"]()

            print(colours)

            pnl.write("update_color", json.dumps(colours).encode('UTF-8'))

        elif command_string == "send_value":
            script_len = int.from_bytes(data[0:4], byteorder=BYTE_ORDER)
            script_name = data[4:script_len + 4].decode('UTF-8')

            function_len = int.from_bytes(data[script_len + 4:script_len + 8], byteorder=BYTE_ORDER)
            function_name = data[script_len + 8:script_len + 8 + function_len + 8].decode('UTF-8')

            value = int.from_bytes(data[script_len + 4:script_len + 8], byteorder=BYTE_ORDER)

            script_dictionary[script_name].dictionary()["dials"][function_name]["function"](value)

        elif command_string == "load_scripts":
            print(data)
            count = int.from_bytes(data[0:4], byteorder=BYTE_ORDER)

            ptr = 4

            for i in range(count):
                length = int.from_bytes(data[ptr:ptr + 4], byteorder=BYTE_ORDER)
                script = data[ptr + 4:ptr + length + 4].decode('UTF-8')

                module = __import__(script)
                # The following line is needed to ensure that the old instance is destroyed BEFORE the new instance is created
                script_dictionary[script] = None
                script_dictionary[script] = getattr(module, "Script")()

                # Setup initial colours
                pnl.write("update_color", json.dumps(script_dictionary[script].colours).encode('UTF-8'))

                print("Loaded: " + script)
                ptr += 4 + length

        elif command_string == "get_page":
            # Since we cannot update the gui from worker threads, we test to see if we are running in the main thread.
            # If we are not, we save the 'get_page' data until the application is taken out of the system tray
            # and the GUI is reloaded.
            if threading.current_thread() == threading.main_thread():
                app.load_combos(data)
            else:
                global last_page
                last_page = data

def create_image(width=32, height=32, color1="red", color2="blue"):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

root = tk.Tk()
app = CtrlPnlHostFrame(root)
thread = None
stop_thread = False

# If the device changes the page while the host program is in the system tray, save the page so we can load it when
# host leaves system tray
last_page = None


def quit_window(icon):
    icon.stop()
    root.destroy()


def show_window(icon):
    global stop_thread
    icon.stop()
    root.after(0,root.deiconify)
    stop_thread = True  # Stop worker thread so that GUI thread can take over
    global last_page
    if last_page:  # update current page if it has changed
        app.load_combos(last_page)


def withdraw_window():
    root.withdraw()
    image = create_image()
    menu = Menu(item('Quit', quit_window), item('Show', show_window, default=True))
    icon = pystray.Icon("name", image, "CtrlPnl", menu)
    icon.run(dostuff)


def dostuff(icon):
    icon.visible = True

    def ticks():
        while True:
            global stop_thread
            if stop_thread:
                stop_thread = False
                break
            tick()

    thread = threading.Thread(target=ticks)
    thread.start()


port = 'COM3'

pnl = CtrlPnlComs(port)

script_dictionary = {}

root.protocol("WM_DELETE_WINDOW", withdraw_window)

app.pack()

app.load_names()

# Start the application in system tray
withdraw_window()

while True:
    if root.children.__len__() != 0:  # if the root object hasn't been destroyed, update GUI and call tick
        app.update_idletasks()
        app.update()
        tick()
    else:  # If root object has been destroyed, stop worker thread and exit
        stop_thread = True
        break


