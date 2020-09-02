

class Script:
    def __init__(self):
        self.equaliser_config_path = "C:\Program Files\EqualizerAPO\config\config.txt"
        self.bass_gain_values = [-40, -20, -10, -8, -4, -2, -1, 0, 1, 2, 4]
        self.current_bass_gain = self.bass_gain_values.index(0)

        self.preamp_gain_values = [-40, -20, -10, -8, -4, -2, -1, 0, 1, 2, 4]
        self.current_preamp_gain = self.preamp_gain_values.index(0)

        self.preamp_ismuted = False
        self.bass_ismuted = False

        self.write_preamp(self.preamp_gain_values[self.current_preamp_gain])
        self.write_bass(self.bass_gain_values[self.current_bass_gain])


    def dictionary(self):
        return {
            "name": "Master Volume controller",
            "buttons":
                {
                    "mute": {
                        "label": "Mute",
                        "function": self.mute_preamp
                    },
                    "volume_up": {
                        "label": "Volume Up",
                        "function": self.volume_up
                    },
                    "volume_down": {
                        "label": "Volume Down",
                        "function": self.volume_down
                    },
                    "mute_bass": {
                        "label": "Mute Bass",
                        "function": self.mute_bass
                    },
                    "bass_up": {
                        "label": "Bass Up",
                        "function": self.bass_up
                    },
                    "bass_down": {
                        "label": "Bass Down",
                        "function": self.bass_down
                    }
                },
            "dials": []
        }

    def write_preamp(self, val):
        bass = ""
        with open(self.equaliser_config_path, "r") as fp:
            first = fp.readline()
            bass = fp.readline()

        print("first: " + first)
        print("second: " + bass)

        preamp = "Preamp: " + str(val) + " dB"

        with open(self.equaliser_config_path, "w") as fp:
            fp.writelines([preamp, "\n" + bass])

        return {"mute": "red"}

    def write_bass(self, val):
        preamp = ""
        with open(self.equaliser_config_path, "r") as fp:
            preamp = fp.readline()

        bass = "GraphicEQ: 25 " + str(val) + "; 40 " + str(val) + "; 63 " + str(val) + "; 100 " + str(val) \
               + "; 160 " + str(val) + "; 250 0; 400 0; 630 0; 1000 0; 1600 0; 2500 0; 4000 0; 6300 0; 10000 0; 16000 0"

        with open(self.equaliser_config_path, "w") as fp:
            fp.writelines([preamp, bass])

        return {"mute": "red"}

    # Button press and dial change functions must return a colour
    def mute_preamp(self):
        print("Mute called")
        self.preamp_ismuted = not self.preamp_ismuted

        if self.preamp_ismuted is True:
            self.write_preamp(-40)
        else:
            self.write_preamp(self.preamp_gain_values[self.current_preamp_gain])

        return {"mute": "green"}

    def volume_up(self):
        self.current_preamp_gain += 1

        if self.current_preamp_gain == self.preamp_gain_values.__len__():
            self.current_preamp_gain = self.preamp_gain_values.__len__() - 1

        self.write_preamp(self.preamp_gain_values[self.current_preamp_gain])

        return {"mute": "red"}

    def volume_down(self):
        self.current_preamp_gain -= 1

        if self.current_preamp_gain == -1:
            self.current_preamp_gain = 0

        self.write_preamp(self.preamp_gain_values[self.current_preamp_gain])

        return {"mute": "red"}

    def mute_bass(self):
        self.bass_ismuted = not self.bass_ismuted

        self.write_bass(-40)

        if self.bass_ismuted is True:
            self.write_bass(-40)
        else:
            self.write_bass(self.bass_gain_values[self.current_bass_gain])

        return {"mute": "red"}

    def bass_up(self):
        print("bass up")
        self.current_bass_gain += 1

        if self.current_bass_gain == self.bass_gain_values.__len__():
            self.current_bass_gain = self.bass_gain_values.__len__() - 1

        self.write_bass(self.bass_gain_values[self.current_bass_gain])

        return {"mute": "red"}

    def bass_down(self):
        self.current_bass_gain -= 1

        if self.current_bass_gain == -1:
            self.current_bass_gain = 0

        self.write_bass(self.bass_gain_values[self.current_bass_gain])

        return {"mute": "red"}
