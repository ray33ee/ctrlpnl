from ctrlpnl import CtrlPnl, CtrlPnlFrame, COMMANDS, BYTE_ORDER

import tkinter as tk

import json

import os

# Make sure host and device do not send commands at the same time

scripts_dir = "./scripts/"

root = tk.Tk()

pnl = CtrlPnl("COM4")

app = CtrlPnlFrame(pnl, master=root)

config = {}

with open("device_config.json", "r") as infile:
    config = json.load(infile)

print(json.dumps(config))

module = __import__("volume_script")

test_script = getattr(module, "Script")

thing = test_script()

print(thing.dictionary())

script_dictionary = {}


def loadPage(index):
    page = config["pages"][0]
    scripts = page["scripts"]
    buttons = page["buttons"]

    print("Scripts: " + str(scripts))

    for i in range(8):
        if buttons[i].__len__() != 0:
            print(buttons[i]["script"])
            print(buttons[i]["function"])
            app.widget_list[i].text(buttons[i]["name"])
            app.widget_list[i].set_function(buttons[i]["script"], buttons[i]["function"])
            app.widget_list[i].enabled(True)
        else:
            app.widget_list[i].enabled(False)

    pnl.load_scripts(scripts)

loadPage(0)

while True:
    app.update_idletasks()
    app.update()
    if pnl.inBufferSize() != 0:
        response = pnl.read()
        command_string = COMMANDS[response["identifier"]]

        if command_string == "open":
            pass
        elif command_string == "remove_page":
            pass
        elif command_string == "add_script":
            len = int.from_bytes(response["data"][0:4], byteorder=BYTE_ORDER)
            title = response["data"][4:len+4].decode(encoding='UTF-8')
            script = response["data"][len+4:]
            with open(os.path.join(scripts_dir, title), "wb") as fp:
                fp.write(script)


        elif command_string == "assign_script":
            pass
        elif command_string == "button_pressed":
            pass
        elif command_string == "dial_changed":
            pass
        elif command_string == "add_page":
            pass

        print(command_string)
        print(response)



