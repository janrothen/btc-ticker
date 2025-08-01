
# LED Strip Light

Feature-rich Raspberry Pi project for controlling an RGB LED strip light. Includes:

- Web-based REST API (Flask) for remote control (on/off, color, brightness, effects)
- Homebridge integration for Apple HomeKit and Siri voice control
- Multiple built-in LED effects (breathing, fade, color cycle, random, and more)
- Time-based color profiles and scheduled automation (systemd, cron)
- Command-line interface for scripting and manual control
- Modular, testable Python codebase with hardware abstraction and full unit test suite

Easily automate, script, or integrate your LED strip with smart home platforms and custom workflows.

The guide ["How to connect RGB Strip LED Lights to Raspberry Pi Zero W"](https://danidudas.medium.com/how-to-connect-rgb-strip-led-lights-to-raspberry-pi-zero-w-and-control-from-node-js-70ddfec19f0b) shows how to physically connect a 12 V RGB strip to a Pi Zero W and drive each color channel from the command line: ￼


## Prerequisites
```
python3  
configparser==7.1.0
python-dateutil==2.8.2
```
## Installing

Create symlink to utils in this directory, or imports won't work.
Configure the scripts: `config.conf`

We use the [pigpio](https://abyz.me.uk/rpi/pigpio/download.html) library for PWM control of the GPIO pins. To install it on your Raspberry Pi:
```bash
sudo apt-get install pigpio
```
then start the service
```
sudo systemctl start pigpiod
```

## Development Setup

### Virtual Environment
Create and activate a virtual environment for development:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

### Running the Application
The application supports multiple effects via command-line arguments:

```bash
# Basic profile effect (morning/evening colors based on time)
./run.py profile

# Breathing effect with custom color and duration
./run.py breathing --color red --duration 3000

# Random color changes
./run.py random --interval 2000

# Color cycling through multiple colors
./run.py cycle --colors red,green,blue,yellow --duration 2500

# Fade between two colors
./run.py fade --from black --to white --duration 5000

# Use hex colors
./run.py breathing --color "#FF6347"

# Get help
./run.py --help
```

### Running Tests
The project includes comprehensive unit tests with hardware mocking:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=led --cov=config --cov=cli --cov=utils

# Run tests with detailed coverage report (generates HTML)
pytest --cov=led --cov=config --cov=cli --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_color.py

# Run tests matching a pattern
pytest -k "test_color"

# Run tests with verbose output
pytest -v

# Skip slow tests
pytest -m "not slow"
```


### Project Structure
```
ledstriplight/
├── etc/
│   ├── systemd.d/               # Systemd service files and installation guide
│   ├── cron.d/                  # Cron job files for scheduled automation
│   └── homebridge/              # Homebridge integration
└── src/                         # Application source code
    ├── run.py                   # Main application entry point
    ├── config_manager.py        # Configuration manager
    ├── http_server.py           # Flask REST API server
    ├── led/                     # Core LED control modules
    │   ├── effects.py           # LED effects (breathing, fade, etc.)
    │   ├── gpio_service.py      # Hardware GPIO interface
    │   ├── led_strip_light_controller.py # Main LED controller
    │   ├── profile_manager.py   # Time-based color profiles
    │   └──effect_runner.py      # Effect runner
    ├── cli/                     
    │   └── cli_handler.py       # Command-line interface handler
    ├── utils/                   # Utilities (logging, shutdown handling)
    └── tests/                   # Unit tests with mocked hardware
```

## REST API (Flask Server)

The project includes a Flask server for remote control via HTTP endpoints:

**Endpoints:**

- `POST /on` — Turn the light on (white)
- `POST /off` — Turn the light off (black)
- `GET /status` — Get on/off state and current color (hex)
- `GET /color` — Get current color (hex)
- `POST /color/<value>` — Set color (hex string or named color)
- `GET /brightness` — Get current brightness (0–100)
- `POST /brightness/<int:value>` — Set brightness (0–100)

Example usage:
```bash
curl -X POST http://localhost:5000/on
curl -X POST http://localhost:5000/color/ff0000
curl -X POST http://localhost:5000/brightness/80
curl http://localhost:5000/status
```

## Homebridge Integration

You can integrate the LED strip with Homebridge for Apple HomeKit support. All installation and configuration instructions, including example Homebridge accessory configuration, can be found in the `etc/homebridge/` directory of this repository.

See [`README.md`](etc/homebridge/README.md) for details on how to set up Homebridge integration and connect it to the Flask server endpoints.
