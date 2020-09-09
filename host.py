from datetime import datetime

from ctrlpnl import CtrlPnl, COMMANDS, BYTE_ORDER, PanelRow, PanelCombos
import json
import tkinter as tk
import os

def new_page_command():
    pnl.write("add_page")


def remove_page_command():
    print("iojoijoij")
    pnl.write("remove_page", b'')
    load_combos()

def next_page_command():
    pnl.write("next_page")


def previous_page_command():
    pnl.write("previous_page")


def get_page_command():
    pnl.write("get_page")

def send_page_command():

    buttons = []

    for combo in combos:
        button = {}
        if combo.script.get() != "":
            button["script"] = combo.script.get()
            button["function"] = combo.function.get()
            index = scripts_and_functions[combo.script.get()]["functions"].index(combo.function.get())
            button["name"] = scripts_and_functions[combo.script.get()]["names"][index]

        buttons.append(button)

    print(buttons)

    page = {
        "title": page_name.get(),
        "buttons": buttons,
        "dials": [
            "",
            "",
            "",
            ""
        ]
    }

    pnl.write("send_page", json.dumps(page).encode('UTF-8'))



port = 'COM4'

pnl = CtrlPnl(port)

script_dictionary = {}


root = tk.Tk()

app = tk.Frame(root)
app.pack()

buttons = tk.Frame(app)
buttons.pack()

new_page = tk.Button(buttons)
new_page["text"] = "new page"
new_page.pack(side="left")
new_page["command"] = new_page_command

remove_page = tk.Button(buttons)
remove_page["text"] = "remove page"
remove_page.pack(side="left")
remove_page["command"] = remove_page_command

send_page = tk.Button(buttons)
send_page["text"] = "send page"
send_page.pack(side="left")
send_page["command"] = send_page_command

next_page = tk.Button(buttons)
next_page["text"] = "next page"
next_page.pack(side="left")
next_page["command"] = next_page_command

previous_page = tk.Button(buttons)
previous_page["text"] = "previous page"
previous_page.pack(side="left")
previous_page["command"] = previous_page_command

get_page = tk.Button(buttons)
get_page["text"] = "get page"
get_page.pack(side="left")
get_page["command"] = get_page_command

page_name = tk.Entry(app)
page_name.pack(side="top")

label1 = tk.Label(app)
label1["text"] = ""
label1.pack(side="top")

row1 = PanelRow(PanelCombos, None, app)
row1.pack(side="top")


label2 = tk.Label(app)
label2["text"] = ""
label2.pack(side="top")

scripts_and_functions = {}

row2 = PanelRow(PanelCombos, None, scripts_and_functions, app)
row2.pack(side="top")

combos = [*row2.widget_list, *row1.widget_list]

i = 0
for combo in combos:
    combo.script.set(str(i))
    i +=1

def load_names():
    global scripts_and_functions

    scripts_and_functions = {
        "":
         {
             "functions": [""],
             "names": [""]
         }
    }
    ls = os.listdir(os.path.dirname(__file__))
    for dir in ls:
        if dir[-10:] == "_script.py":
            script_name = dir[:-3]
            module = __import__(script_name)
            functions = getattr(module, "Script").functions()
            names = getattr(module, "Script").names()
            scripts_and_functions[script_name] = { "functions": functions, "names": names }

    for combo in combos:
        combo.scripts_and_functions = scripts_and_functions
    print(scripts_and_functions)

def load_combos():
    page = json.loads(data.decode('UTF-8'))

    index = 0
    page_name.delete(0, tk.END)
    page_name.insert(0, page["title"])
    for button in page["buttons"]:
        combos[index].script["values"] = list(scripts_and_functions.keys())

        if len(button) != 0:
            combos[index].set_script(button["script"], button["function"])
        else:
            combos[index].set_script("", "")

        index += 1

load_names()

while True:
    app.update_idletasks()
    app.update()
    if pnl.inBufferSize() != 0:
        response = pnl.read()
        command_string = COMMANDS[response["identifier"]]
        data = response["data"]

        if command_string == "send_function":
            script_len = int.from_bytes(data[0:4], byteorder=BYTE_ORDER)
            script_name = data[4:script_len+4].decode('UTF-8')
            function_len = int.from_bytes(data[script_len+4:script_len+8], byteorder=BYTE_ORDER)
            function_name = data[script_len+8:script_len+8 + script_len+8].decode('UTF-8')

            print("Script :" + script_name)
            print("Function :" + function_name)

            colours = script_dictionary[script_name].dictionary()["buttons"][function_name]["function"]()

            print(colours)

            pnl.write("update_color", json.dumps(colours).encode('UTF-8'))

        elif command_string == "load_scripts":
            print(data)
            count = int.from_bytes(data[0:4], byteorder=BYTE_ORDER)

            ptr = 4

            for i in range(count):
                length = int.from_bytes(data[ptr:ptr+4], byteorder=BYTE_ORDER)
                script = data[ptr+4:ptr+length+4].decode('UTF-8')

                module = __import__(script)
                script_dictionary[script] = getattr(module, "Script")()

                # Setup initial colours
                pnl.write("update_color", json.dumps(script_dictionary[script].colours).encode('UTF-8'))

                print("Loaded: " + script)
                ptr += 4+length

        elif command_string == "get_page":
            load_combos()
