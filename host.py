from ctrlpnl import CtrlPnl, COMMANDS, BYTE_ORDER
import json

port = 'COM4'

pnl = CtrlPnl(port)

script_dictionary = {}

while True:
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

                print(script)
                ptr += 4+length

        elif command_string == "add_script":
            pass
