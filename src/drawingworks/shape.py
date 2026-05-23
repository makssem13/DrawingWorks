# shape.py - realization of shapes
# part of DrawingWorks project
# licensed under GNU General Public License version 3 or higher

from dataclasses import dataclass, field
from .cms import Color
from enum import Enum, auto

class ShapeType(Enum):
    POINT = auto()
    LINE = auto()
    CIRCLE = auto()
    OVAL = auto()
    RECT = auto()
    SKIP = auto()

@dataclass
class Shape:
    z: int
    points = field(default_factory=list)
    FillColor: Color
    BorderColor: Color
