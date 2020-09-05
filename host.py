from ctrlpnl import CtrlPnl, COMMANDS, BYTE_ORDER
import json
import tkinter as tk


def new_page_command():
    pnl.write("add_page")

def remove_page_command():
    print("iojoijoij")
    pnl.write("remove_page", b'')


def send_page_command():
    page = {
            "title": "Volume",
            "scripts": [
                "volume_script"
            ],
            "buttons": [
                {
                    "script": "volume_script",
                    "function": "mute",
                    "name": "Mute"
                },
                {
                    "script": "volume_script",
                    "function": "volume_up",
                    "name": "Volume Up"
                },
                {
                    "script": "volume_script",
                    "function": "volume_down",
                    "name": "Volume Down"
                },
                {},
                {
                    "script": "volume_script",
                    "function": "mute_bass",
                    "name": "Mute bass"
                },
                {
                    "script": "volume_script",
                    "function": "bass_up",
                    "name": "Bass up"
                },
                {
                    "script": "volume_script",
                    "function": "bass_down",
                    "name": "Bass down"
                },
                {}
            ],
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

new_page = tk.Button(app)
new_page["text"] = "new page"
new_page.pack(side="left")
new_page["command"] = new_page_command

remove_page = tk.Button(app)
remove_page["text"] = "remove page"
remove_page.pack(side="left")
remove_page["command"] = remove_page_command

send_page = tk.Button(app)
send_page["text"] = "send page"
send_page.pack(side="left")
send_page["command"] = send_page_command

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

        elif command_string == "add_script":
            pass
