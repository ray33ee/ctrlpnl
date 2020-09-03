from time import sleep

class Script:
    def __init__(self):
        self.equaliser_config_path = "C:\Program Files\EqualizerAPO\config\config.txt"

        self.preamp_colours = ['#E8F8F5', '#D1F2EB', '#A3E4D7', '#76D7C4', '#48C9B0', '#1ABC9C', '#17A589', '#148F77', '#117864', '#0E6251', '#0A463A']
        self.bass_colours = ['#F4ECF7', '#E8DAEF', '#D2B4DE', '#BB8FCE', '#A569BD', '#8E44AD', '#7D3C98', '#6C3483', '#5B2C6F', '#4A235A', '#2F1739']

        self.bass_gain_values = [-40, -20, -10, -8, -4, -2, -1, 0, 1, 2, 4]
        self.current_bass_gain = self.bass_gain_values.index(0)

        self.preamp_gain_values = [-40, -20, -10, -8, -4, -2, -1, 0, 1, 2, 4]
        self.current_preamp_gain = self.preamp_gain_values.index(0)

        self.preamp_ismuted = False
        self.bass_ismuted = False

        self.colours = self.write()


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



    def get_color(self, pallette, ismuted, gain):
        if ismuted:
            return "red"
        else:
            return pallette[gain]

    def write(self):

        if self.preamp_ismuted is True:
            pre_val = -40
        else:
            pre_val = self.preamp_gain_values[self.current_preamp_gain]

        if self.bass_ismuted is True:
            bass_val = -40
        else:
            bass_val = self.bass_gain_values[self.current_bass_gain]

        preamp = "Preamp: " + str(pre_val) + " dB\n"

        bass = "GraphicEQ: 25 " + str(bass_val) + "; 40 " + str(bass_val) + "; 63 " + str(bass_val) + "; 100 " + str(bass_val) \
               + "; 160 " + str(bass_val) + "; 250 0; 400 0; 630 0; 1000 0; 1600 0; 2500 0; 4000 0; 6300 0; 10000 0; 16000 0\n"

        with open(self.equaliser_config_path, "w") as fp:
            fp.writelines([preamp, bass])

        preamp_col = self.get_color(self.preamp_colours, self.preamp_ismuted, self.current_preamp_gain)
        bass_col = self.get_color(self.bass_colours, self.bass_ismuted, self.current_bass_gain)
        return {"mute": preamp_col, "volume_up": preamp_col, "volume_down": preamp_col,
                "mute_bass": bass_col, "bass_up": bass_col, "bass_down": bass_col}


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

        return self.write()

    def volume_up(self):
        self.preamp_ismuted = False

        self.current_preamp_gain += 1

        if self.current_preamp_gain == self.preamp_gain_values.__len__():
            self.current_preamp_gain = self.preamp_gain_values.__len__() - 1

        return self.write()

    def volume_down(self):
        self.preamp_ismuted = False

        self.current_preamp_gain -= 1

        if self.current_preamp_gain == -1:
            self.current_preamp_gain = 0

        return self.write()

    def mute_bass(self):
        self.bass_ismuted = not self.bass_ismuted

        return self.write()

    def bass_up(self):
        self.bass_ismuted = False

        self.current_bass_gain += 1

        if self.current_bass_gain == self.bass_gain_values.__len__():
            self.current_bass_gain = self.bass_gain_values.__len__() - 1

        return self.write()

    def bass_down(self):
        self.bass_ismuted = False

        self.current_bass_gain -= 1

        if self.current_bass_gain == -1:
            self.current_bass_gain = 0

        return self.write()
