#!/usr/bin/env python3

import random
from typing import Any, Tuple, Optional, ClassVar
from dataclasses import dataclass, field

MIN_COLOR_VALUE: int = 0
MAX_COLOR_VALUE: int = 255


@dataclass(frozen=True, eq=True)
class Color:
    """
    Represents an RGB color with validation and utility methods.
    
    Provides a clean interface for working with RGB colors, including
    predefined color constants, validation, and conversion methods.
    
    Usage:
        red = Color(255, 0, 0)
        green = Color.GREEN
        custom = Color.from_hex("#FF5733")
        r, g, b = red.rgb  # Unpack as tuple
    """
    red: int = field(default=0)
    green: int = field(default=0)
    blue: int = field(default=0)

    BLACK: ClassVar[Optional['Color']]
    WHITE: ClassVar[Optional['Color']]
    RED: ClassVar[Optional['Color']]
    GREEN: ClassVar[Optional['Color']]
    BLUE: ClassVar[Optional['Color']]
    YELLOW: ClassVar[Optional['Color']]
    CYAN: ClassVar[Optional['Color']]
    MAGENTA: ClassVar[Optional['Color']]
    ORANGE: ClassVar[Optional['Color']]
    PURPLE: ClassVar[Optional['Color']]
    PINK: ClassVar[Optional['Color']]
    WARM_WHITE: ClassVar[Optional['Color']]
    COOL_WHITE: ClassVar[Optional['Color']]

    def __post_init__(self):
        object.__setattr__(self, 'red', self._clamp(self.red))
        object.__setattr__(self, 'green', self._clamp(self.green))
        object.__setattr__(self, 'blue', self._clamp(self.blue))

    @staticmethod
    def _clamp(value: Any) -> int:
        """Clamp color value between MIN and MAX."""
        return max(MIN_COLOR_VALUE, min(MAX_COLOR_VALUE, int(value)))

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Return color as (red, green, blue) tuple."""
        return (self.red, self.green, self.blue)
    
    @classmethod
    def from_tuple(cls, rgb_tuple: Tuple[int, int, int]) -> 'Color':
        """Create Color from (r, g, b) tuple."""
        return cls(*rgb_tuple)
    
    @classmethod
    def from_hex(cls, hex_string: str) -> 'Color':
        """Create Color from hex string like '#FF0000' or 'FF0000'."""
        hex_string = hex_string.lstrip('#')
        if len(hex_string) != 6:
            raise ValueError("Hex string must be 6 characters")
        
        try:
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
            return cls(r, g, b)
        except ValueError:
            raise ValueError("Invalid hex color string")
    
    @classmethod
    def random(cls) -> 'Color':
        """Create a random color with RGB values between 0-255."""
        red = random.randint(MIN_COLOR_VALUE, MAX_COLOR_VALUE)
        green = random.randint(MIN_COLOR_VALUE, MAX_COLOR_VALUE)
        blue = random.randint(MIN_COLOR_VALUE, MAX_COLOR_VALUE)
        return cls(red, green, blue)
    
    @classmethod
    def random_bright(cls, min_brightness: int = 100) -> 'Color':
        """Create a random bright color with minimum brightness per channel."""
        red = random.randint(min_brightness, MAX_COLOR_VALUE)
        green = random.randint(min_brightness, MAX_COLOR_VALUE)
        blue = random.randint(min_brightness, MAX_COLOR_VALUE)
        return cls(red, green, blue)
    
    @classmethod
    def random_pastel(cls) -> 'Color':
        """Create a random pastel color (lighter, softer colors)."""
        red = random.randint(150, MAX_COLOR_VALUE)
        green = random.randint(150, MAX_COLOR_VALUE)
        blue = random.randint(150, MAX_COLOR_VALUE)
        return cls(red, green, blue)

    def is_black(self) -> bool:
        """Check if the color is black (all channels are 0)."""
        return self.red == 0 and self.green == 0 and self.blue == 0

    def max_channel(self) -> int:
        """Return the maximum channel value (R, G, or B)."""
        return max(self.red, self.green, self.blue)

    def to_hex(self) -> str:
        """Return the color as a hex string (e.g. '#ff00ff')."""
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)

    def __str__(self) -> str:
        return f"Color(R={self.red}, G={self.green}, B={self.blue})"
    
    def __repr__(self) -> str:
        return f"Color({self.red}, {self.green}, {self.blue})"
    
    # Predefined colors
    BLACK = None
    WHITE = None
    RED = None
    GREEN = None
    BLUE = None
    YELLOW = None
    CYAN = None
    MAGENTA = None
    ORANGE = None
    PURPLE = None
    PINK = None
    WARM_WHITE = None
    COOL_WHITE = None

# Initialize predefined colors
Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.RED = Color(255, 0, 0)
Color.GREEN = Color(0, 255, 0)
Color.BLUE = Color(0, 0, 255)
Color.YELLOW = Color(255, 255, 0)
Color.CYAN = Color(0, 255, 255)
Color.MAGENTA = Color(255, 0, 255)
Color.ORANGE = Color(255, 165, 0)
Color.PURPLE = Color(128, 0, 128)
Color.PINK = Color(255, 192, 203)
Color.WARM_WHITE = Color(255, 200, 100)
Color.COOL_WHITE = Color(200, 220, 255)