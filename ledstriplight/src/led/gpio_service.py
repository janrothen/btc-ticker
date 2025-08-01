#!/usr/bin/env python3

import subprocess
import logging
from typing import Any

MIN_PWM_VALUE: int = 0
MAX_PWM_VALUE: int = 255


class GPIOService:
    """
    Service for controlling GPIO pins on Raspberry Pi using pigpio daemon.
    
    This service provides an abstraction layer for hardware interactions,
    specifically for controlling LED brightness through PWM (Pulse Width Modulation).
    Uses the pigpio library via shell commands to set PWM values on GPIO pins.
    
    Typical usage:
        gpio = GPIOService()
        gpio.set_pin_pwm(17, 127)  # Set pin 17 to 50% brightness
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def get_pin_pwm(self, pin: int) -> int:
        """Get the current PWM value for a specific GPIO pin using pigpio."""
        try:
            result = subprocess.run(["pigs", "gdc", str(pin)], capture_output=True, check=True, text=True)
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            logging.error(f"Error reading pin {pin}: {e}")
            return -1

    def set_pin_pwm(self, pin: int, value: int) -> None:
        """Set pulse width modulation value for a specific GPIO pin using pigpio."""
        rounded = self._clamp_value(value)
        try:
            subprocess.run(["pigs", "p", str(pin), str(rounded)], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set pin {pin}: {e}")

    def _clamp_value(self, value: Any, min_val: int = MIN_PWM_VALUE, max_val: int = MAX_PWM_VALUE) -> int:
        """Clamp value between min and max bounds."""
        rounded = int(round(value))
        if rounded < min_val:
            rounded = min_val
        if rounded > max_val:
            rounded = max_val
        return rounded