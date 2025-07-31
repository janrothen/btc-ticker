
# LED Strip Light

Feature-rich Raspberry Pi project for controlling an RGB LED strip light. Includes:

- Web-based REST API (Flask) for remote control (on/off, color, brightness, effects)
- Homebridge integration for Apple HomeKit and Siri voice control
- Multiple built-in LED effects (breathing, fade, color cycle, random, and more)
- Time-based color profiles and scheduled automation (systemd, cron)
- Command-line interface for scripting and manual control
- Modular, testable Python codebase with hardware abstraction and full unit test suite

Easily automate, script, or integrate your LED strip with smart home platforms and custom workflows.

### run.py
Turns on the LED strip light with a color configured in config.conf.

https://danidudas.medium.com/how-to-connect-rgb-strip-led-lights-to-raspberry-pi-zero-w-and-control-from-node-js-70ddfec19f0b

## Prerequisites
```
python3  
configparser==7.1.0
python-dateutil==2.8.2
```
## Installing

Create symlink to utils in this directory, or imports won't work.
Configure the scripts: `config.conf`

Follow the pigpio installation instructions:
```
https://abyz.me.uk/rpi/pigpio/download.html
```
or
`sudo apt-get install pigpio`

### 
```
$ sudo systemctl start pigpiod
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
├── led/                   # Core LED control modules
│   ├── color.py           # Color management
│   ├── effects.py         # LED effects (breathing, fade, etc.)
│   ├── gpio_service.py    # Hardware GPIO interface
│   ├── led_strip_light_controller.py # Main LED controller
│   └── profile_manager.py # Time-based color profiles
├── config/                # Configuration management
│   └── homebridge/        # Homebridge configuration
├── cli/                   # Command-line interface
├── utils/                 # Utilities (logging, shutdown handling)
├── tests/                 # Unit tests with mocked hardware
├── service/               # Systemd service files
├── http_server.py         # Flask REST API server
└── run.py                 # Main application entry point
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

You can integrate the LED strip with Homebridge for Apple HomeKit support. All installation and configuration instructions, including example Homebridge accessory configuration, can be found in the `config/homebridge/` directory of this repository.

See [`README.md`](config/homebridge/README.md) for details on how to set up Homebridge integration and connect it to the Flask server endpoints.

## Timers

Copy `led.service` to `/etc/systemd/system`

Create a file in `/etc/cron.d/led` to start/stop the systemd service.
```
/etc/cron.d $ cat led  
15 19 * * * root /bin/systemctl start led 2>/tmp/error
30 22 * * * root /bin/systemctl stop led 2>/tmp/error

15 06 * * * root /bin/systemctl start led 2>/tmp/error
30 08 * * * root /bin/systemctl stop led 2>/tmp/error
```

### Status
```
pi@zero:~ $ systemctl status led.service
● led.service - LED Strip Controller Service
     Loaded: loaded (/etc/systemd/system/led.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2025-07-31 17:05:02 CEST; 2h 40min ago
   Main PID: 9680 (python3)
      Tasks: 1 (limit: 414)
        CPU: 1min 32.221s
     CGroup: /system.slice/led.service
             └─9680 /usr/bin/python3 -u run.py profile
```
