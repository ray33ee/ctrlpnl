from ctrlpnl import CtrlPnl, CtrlPnlFrame, COMMANDS, BYTE_ORDER

import tkinter as tk

# Make sure host and device do not send commands at the same time

root = tk.Tk()

app = CtrlPnlFrame("COM3", "device_config.json", master=root)

while True:
    app.update_idletasks()
    app.update()




