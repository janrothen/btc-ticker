#!/usr/bin/env python3

import logging
from threading import Thread
from typing import Any, Callable, Optional, Dict
from .color import Color
from .gpio_service import GPIOService

R: str = 'red'
G: str = 'green'
B: str = 'blue'


class LEDStripLightController(object):
    def __init__(self, pins: Dict[str, int], gpio_service: Optional[GPIOService] = None) -> None:
        self._gpio_service = gpio_service or GPIOService()
        self._pins = pins

        self._interrupt = False
        self._sequence = None

    def switch_on(self) -> None:
        self.set_color(Color.WARM_YELLOW)

    def switch_off(self) -> None:
        self.interrupt()
        self.set_color(Color.BLACK)
        self.resume()

    def interrupt(self) -> None:
        self._interrupt = True

    def resume(self) -> None:
        self._interrupt = False

    def is_on(self) -> bool:
        return not self.get_color().is_black()

    def is_interrupted(self) -> bool:
        """Check if the current sequence should be interrupted."""
        return self._interrupt

    def get_color(self) -> Color:
        red = self._gpio_service.get_pin_pwm(self._pins[R])
        green = self._gpio_service.get_pin_pwm(self._pins[G])
        blue = self._gpio_service.get_pin_pwm(self._pins[B])
        return Color(red, green, blue)

    def set_color(self, color: Color = Color.WARM_YELLOW) -> None:
        logging.info(f"Set RGB to: R={color.red:6.2f} G={color.green:6.2f} B={color.blue:6.2f}")
        self._set_red_value(color.red)
        self._set_green_value(color.green)
        self._set_blue_value(color.blue)
    
    def get_brightness_percentage(self) -> int:
        """Estimate brightness percentage (0–100%) based on current RGB values."""
        current_color = self.get_color()
        if current_color.is_black():
            return 0
        r = current_color.red
        g = current_color.green
        b = current_color.blue
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        # Convert to 0–100%
        return round(luminance / 255 * 100)

    def set_brightness(self, brightness: int) -> None:
        """
        Set brightness (0–100%) while keeping the same color hue.
        Scales current RGB values proportionally.
        """
        if not (0 <= brightness <= 100):
            raise ValueError("Brightness must be between 0 and 100")

        current_color = self.get_color()
        r_current = current_color.red
        g_current = current_color.green
        b_current = current_color.blue

        current_max = current_color.max_channel()
        if current_color.is_black():
            r_new = g_new = b_new = int(255 * (brightness / 100))
        else:
            scale = (brightness / 100) * (255 / current_max)
            r_new = int(r_current * scale)
            g_new = int(g_current * scale)
            b_new = int(b_current * scale)

        self.set_color(Color.from_tuple((r_new, g_new, b_new)))

    #region Sequence control
    def run_sequence(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.stop_current_sequence()
        self.start_sequence(func, *args, **kwargs)

    def start_sequence(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        logging.info(f"Starting sequence: {func.__name__}")
        self._sequence = Thread(target=func, args=args, kwargs=kwargs)
        self.resume()
        self._sequence.start()

    def stop_current_sequence(self, timeout: int = 60) -> None:
        if self._sequence is None:
            logging.info("No sequence to stop.")
            return
        
        logging.info(f"Stopping sequence: {self._sequence.name}")
        self.interrupt()
        try:
            self._sequence._sequence_stop_signal = True
            self._sequence.join(timeout)
        except AttributeError:
            pass

        self._reset_sequence()
    #endregion

    #region Private basic
    def _set_red_value(self, value: int) -> None:
        self._gpio_service.set_pin_pwm(self._pins[R], value)

    def _set_green_value(self, value: int) -> None:
        self._gpio_service.set_pin_pwm(self._pins[G], value)

    def _set_blue_value(self, value: int) -> None:
        self._gpio_service.set_pin_pwm(self._pins[B], value)

    def _reset_sequence(self) -> None:
        self._sequence = None
    #endregion