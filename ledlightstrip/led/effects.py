#!/usr/bin/env python3

import logging
from time import sleep

from led.color import Color

FADE_STEP_MS = 20.0  # 20 ms per step equals around 100Hz
DEFAULT_EFFECT_DURATION_MS = 2000  # Default duration in milliseconds


def breathing_effect(strip, color=Color.RED, duration=DEFAULT_EFFECT_DURATION_MS):
    """Creates a breathing effect by fading in and out"""
    while not strip._interrupt:
        # Fade in
        fade_effect(strip, Color.BLACK, color, duration)
        if strip.is_interrupted():
            break
        
        # Fade out
        fade_effect(strip, color, Color.BLACK, duration)
        if strip.is_interrupted():
            break

def random_color_effect(strip, interval=DEFAULT_EFFECT_DURATION_MS):
    """Changes colors randomly at specified intervals"""
    while not strip.is_interrupted():
        color = Color.random_bright()
        strip.set_color(color)
        sleep(interval / 1000.0)  # Convert ms to seconds

def color_cycle_effect(strip, colors=[Color.RED, Color.GREEN, Color.BLUE], duration=DEFAULT_EFFECT_DURATION_MS):
    """Cycles through a list of colors"""
    while not strip.is_interrupted():
        for color in colors:
            if strip.is_interrupted():
                break
            fade_effect(strip, Color.BLACK, color, duration)
            sleep(1)  # Hold color for 1 second

def fade_effect(strip, color_start=Color.BLACK, color_end=Color.WHITE, duration=DEFAULT_EFFECT_DURATION_MS):
    r_start, g_start, b_start = color_start.rgb
    r_end, g_end, b_end = color_end.rgb
    r_diff = r_end - r_start
    g_diff = g_end - g_start
    b_diff = b_end - b_start

    steps = int(float(duration) / FADE_STEP_MS)

    logging.info(f"Fading from R={r_start:6.2f} G={g_start:6.2f} B={b_start:6.2f}")
    logging.info(f"         to R={r_end:6.2f} G={g_end:6.2f} B={b_end:6.2f}")
    logging.info(f"         in {steps} steps")

    for step in range(0, steps):
        logging.info(f"Step {step + 1}/{steps}")
        if strip.is_interrupted():
            logging.info("Fading interrupted")
            return
        increment = float(step) / steps
        r_current = r_start + (r_diff * increment)
        g_current = g_start + (g_diff * increment)
        b_current = b_start + (b_diff * increment)
        color_current = Color.from_tuple((int(r_current), int(g_current), int(b_current)))
        strip.set_color(color_current)
        sleep(FADE_STEP_MS / 1000.0)  # Convert ms to seconds

    logging.info(f"Fade completed to R={r_end:6.2f} G={g_end:6.2f} B={b_end:6.2f}")
    strip.set_color(color_end)