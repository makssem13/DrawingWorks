# cms.py - Color Management System
# part if DrawingWorks project
# licensed under GNU General Public Licenve version 3 or higher

from enum import Enum, auto

class ColorMode(Enum):
    RGB = auto()
    CMYK = auto()
    HSV = auto()
    Pantone = auto()

class Color:
    def __init__(self, ColorMode, color):
        self.color = color
        self.mode = ColorMode
    
    def get_hex(self):
        match self.mode:
            case ColorMode.RGB:
                return "#{int(self.color[0]):02x}{int(self.color[1]):02x}{int(self.color[2]):02x}"
            case _:
                raise ValueError("Currently not supported :)")
