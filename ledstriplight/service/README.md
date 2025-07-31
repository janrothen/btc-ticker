# LED Service Installation Guide

## Overview
This systemd service runs the LED strip light controller application as a background daemon on your Raspberry Pi.

## Prerequisites
- Raspberry Pi with Raspberry Pi OS
- Python 3.x installed
- pigpio daemon installed and running
- LED strip light application files in `/home/pi/raspberry/ledstriplight/`

## Installation Steps

### 1. Install the Service File
Copy the service file to the systemd directory:
```bash
sudo cp led.service /etc/systemd/system/
```

### 2. Set Proper Permissions
```bash
sudo chmod 644 /etc/systemd/system/led.service
```

### 3. Reload Systemd
Tell systemd to reload its configuration:
```bash
sudo systemctl daemon-reload
```

### 4. Enable the Service
Enable the service to start automatically on boot:
```bash
sudo systemctl enable led.service
```

### 5. Start the Service
Start the service immediately:
```bash
sudo systemctl start led.service
```

## Service Management Commands

| Command | Description |
|---------|-------------|
| `sudo systemctl start led.service` | Start the service |
| `sudo systemctl stop led.service` | Stop the service |
| `sudo systemctl restart led.service` | Restart the service |
| `sudo systemctl status led.service` | Check service status |
| `sudo systemctl enable led.service` | Enable auto-start on boot |
| `sudo systemctl disable led.service` | Disable auto-start on boot |

## Monitoring and Troubleshooting

### View Service Status
```bash
sudo systemctl status led.service
```

### View Live Logs
```bash
sudo journalctl -u led.service -f
```

### View Recent Logs
```bash
sudo journalctl -u led.service --since "1 hour ago"
```

### View All Logs
```bash
sudo journalctl -u led.service --no-pager
```

## Configuration Notes

- **Working Directory**: The service runs from `/home/pi/raspberry/ledstriplight/`
- **User**: Runs as the `pi` user (not root for security)
- **Auto-restart**: The service will automatically restart if it crashes
- **Dependencies**: Waits for network and pigpio daemon to be ready
- **Graceful Shutdown**: Uses SIGTERM for clean shutdown with 30-second timeout

## Troubleshooting

### Service Won't Start
1. Check if the working directory exists: `ls -la /home/pi/raspberry/ledstriplight/`
2. Check if `run.py` is executable: `ls -la /home/pi/raspberry/led/run.py`
3. Verify pigpio is running: `sudo systemctl status pigpiod`
4. Check for Python errors: `sudo journalctl -u led.service`

### Permission Issues
If you get permission errors, ensure:
- The `pi` user owns the application files: `sudo chown -R pi:pi /home/pi/raspberry/ledstriplight/`
- The `pi` user is in the `gpio` group: `sudo usermod -a -G gpio pi`

### Service Keeps Restarting
Check the logs for errors:
```bash
sudo journalctl -u led.service --since "10 minutes ago"
```

## Uninstalling

To remove the service:
```bash
sudo systemctl stop led.service
sudo systemctl disable led.service
sudo rm /etc/systemd/system/led.service
sudo systemctl daemon-reload
```