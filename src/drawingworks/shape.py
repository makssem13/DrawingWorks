# shape.py - realization of shapes
# part of DrawingWorks project
# licensed under GNU General Public License version 3 or higher

from dataclasses import dataclass, field
from .cms import Color
from enum import Enum, auto
from typing import Optional

class ShapeType(Enum):
    POINT = auto()
    LINE = auto()
    CIRCLE = auto()
    OVAL = auto()
    RECT = auto()
    SKIP = auto()
    POLYGON = auto()

@dataclass
class Shape:
    Type: ShapeType
    z: int
    points: list
    FillColor: Color
    BorderColor: Color
    BorderWidth: int
    Radius: Optional[int] = None
    NoFill: Optional[bool] = False
