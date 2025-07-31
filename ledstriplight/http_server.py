#!/usr/bin/env python3

from flask import Flask, request, jsonify
from config.config_manager import ConfigManager
from led.led_strip_light_controller import LEDStripLightController
from led.color import Color

app = Flask(__name__)
config_manager = ConfigManager()
pins = config_manager.get_all_pin_assignments()
light = LEDStripLightController(pins)

@app.route("/on", methods=["POST"])
def turn_on():
    light.switch_on()
    return jsonify({"status": "on"}), 200

@app.route("/off", methods=["POST"])
def turn_off():
    light.switch_off()
    return jsonify({"status": "off"}), 200

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({
        "on": light.is_on(),
        "color": light.get_color().to_hex()
    }), 200

@app.route("/color", methods=["GET"])
def get_color_txt():
    hex_color = light.get_color().to_hex().lstrip("#").upper()
    return hex_color, 200, {"Content-Type": "text/plain"}

@app.route("/color/<value>", methods=["POST"])
def set_color(value):
    color_str = value.strip().lstrip("#")
    try:
        if len(color_str) == 6:
            color = Color.from_hex("#" + color_str)
        else:
            color = getattr(Color, color_str.upper())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    light.set_color(color)
    return jsonify({"status": "color set", "color": color_str}), 200

@app.route("/brightness", methods=["GET"])
def get_brightness_txt():
    value = light.get_brightness()
    return str(value), 200, {"Content-Type": "text/plain"}

@app.route("/brightness/<int:value>", methods=["POST"])
def set_brightness(value):
    light.set_brightness(value)
    return jsonify({"status": "brightness set", "value": value}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)