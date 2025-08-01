#!/usr/bin/env python3

import configparser
import os
from typing import Tuple, Dict

PINS = 'pins'
R = 'red'
G = 'green'
B = 'blue'
COLOR_CHANNELS = (R, G, B)


class ConfigManager:
    """
    Configuration manager for LED strip light application.
    
    Provides a structured interface to access configuration values from config.conf,
    including GPIO pin assignments and color profiles for different times of day.
    
    The configuration file supports:
    - GPIO pin assignments for RGB channels
    - Morning and evening color profiles with RGB values (0-255)
    
    Usage:
        config = ConfigManager()
        red_pin = config.get_pin('red')
        morning_color = config.get_profile_color('profile.morning')
    """
    
    def __init__(self, config_file: str = '../config.conf') -> None:
        self._config = configparser.ConfigParser()
        self._config_file = config_file
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self._config_file):
            raise FileNotFoundError(f"Configuration file '{self._config_file}' not found")
        
        self._config.read(self._config_file)
    
    def get_profile_colors(self, profile: str) -> Tuple[int, int, int]:
        """
        Get RGB color values for a specific profile.
        
        Args:
            profile: Profile name (e.g., 'profile.morning', 'profile.evening')
            
        Returns:
            Tuple of (red, green, blue) values (0-255)
            
        Raises:
            ValueError: If profile is not found or invalid
        """
        try:
            red = self._config.getint(profile, R)
            green = self._config.getint(profile, G)
            blue = self._config.getint(profile, B)
            return (red, green, blue)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ValueError(f"Profile '{profile}' not found or incomplete: {e}")
    
    def get_profile_color_value(self, profile: str, color: str) -> int:
        """
        Get specific color value from a profile.
        
        Args:
            profile: Profile name (e.g., 'profile.morning')
            color: Color channel ('red', 'green', or 'blue')
            
        Returns:
            Color value (0-255)
        """
        try:
            return self._config.getint(profile, color)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ValueError(f"Color '{color}' in profile '{profile}' not found: {e}")

    def get_all_pin_assignments(self) -> Dict[str, int]:
        """Get all pin assignments as a dictionary."""
        return {
            R: self._get_pin(R),
            G: self._get_pin(G),
            B: self._get_pin(B)
        }
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def _get_pin(self, color: str) -> int:
        """
        Get GPIO pin number for a specific color channel.
        
        Args:
            color: Color channel ('red', 'green', or 'blue')
            
        Returns:
            GPIO pin number
            
        Raises:
            ValueError: If color is not valid or pin not configured
        """
        valid_colors = COLOR_CHANNELS
        if color not in valid_colors:
            raise ValueError(f"Invalid color '{color}'. Must be one of: {valid_colors}")
        
        try:
            return self._config.getint(PINS, color)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ValueError(f"Pin configuration for '{color}' not found: {e}")    