#!/usr/bin/env python3

from flask import Flask, Response, jsonify
from config_manager import ConfigManager
from led.led_strip_light_controller import LEDStripLightController
from led.color import Color

app = Flask(__name__)
config_manager = ConfigManager()
pins = config_manager.get_all_pin_assignments()
led_controller = LEDStripLightController(pins)

@app.route("/on", methods=["POST"])
def turn_on():
    led_controller.switch_on()
    return Response(status=200)

@app.route("/off", methods=["POST"])
def turn_off():
    led_controller.switch_off()
    return Response(status=200)

@app.route("/status", methods=["GET"])
def get_status():
    is_on = "1" if led_controller.is_on() else "0"
    return Response(is_on, status=200)

@app.route("/color", methods=["GET"])
def get_color_txt():
    hex_color = led_controller.get_color().to_hex_with_hash()
    return Response(hex_color, status=200)

@app.route("/color/<value>", methods=["POST"])
def set_color(value):
    color = Color.from_hex(value)
    led_controller.set_color(color)
    return Response(status=200)

@app.route("/brightness", methods=["GET"])
def get_brightness_txt():
    brightness = led_controller.get_brightness_percentage()
    return Response(str(brightness), status=200)

@app.route("/brightness/<int:value>", methods=["POST"])
def set_brightness(value):
    led_controller.set_brightness(value)
    return Response(status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)