import win32api

VK_MEDIA_PLAY_PAUSE = 0xB3

class Script:

    def __init__(self):

        self.colours = {"pause": "yellow"}

        self.pause_code = (0xB3, win32api.MapVirtualKey(0xB3, 0))
        self.stop_code = (0xB2, win32api.MapVirtualKey(0xB2, 0))
        self.mute_code = (0xAD, win32api.MapVirtualKey(0xAD, 0))
        self.up_code = (0xAF, win32api.MapVirtualKey(0xAF, 0))
        self.down_code = (0xAE, win32api.MapVirtualKey(0xAE, 0))
        self.next_code = (0xB0, win32api.MapVirtualKey(0xB0, 0))
        self.previous_code = (0xB1, win32api.MapVirtualKey(0xB1, 0))

    def __del__(self):
        print("DESTROYED!!1!")

    def functions():
        return ["pause", "stop", "mute", "up", "down", "next", "previous"]

    def names():
        return ["Pause", "Stop", "Mute", "Volume Up", "Volume Down", "Next", "Previous"]

    def dictionary(self):
        return {
            "name": "Multimedia keys",
            "buttons":
                {
                    "pause": {
                        "label": "Pause",
                        "function": self.pause
                    },
                    "stop": {
                        "label": "Stop",
                        "function": self.stop
                    },
                    "mute": {
                        "label": "Mute",
                        "function": self.mute
                    },
                    "up": {
                        "label": "Volume Up",
                        "function": self.up
                    },
                    "down": {
                        "label": "Volume Down",
                        "function": self.down
                    },
                    "next": {
                        "label": "Next",
                        "function": self.next
                    },
                    "previous": {
                        "label": "Previous",
                        "function": self.previous
                    },
                },
            "dials": []
        }

    def pause(self):
        win32api.keybd_event(*self.pause_code)

    def stop(self):
        win32api.keybd_event(*self.stop_code)

    def mute(self):
        win32api.keybd_event(*self.mute_code)

    def up(self):
        win32api.keybd_event(*self.up_code)

    def down(self):
        win32api.keybd_event(*self.down_code)

    def next(self):
        win32api.keybd_event(*self.next_code)

    def previous(self):
        win32api.keybd_event(*self.previous_code)
