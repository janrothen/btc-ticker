#!/usr/bin/env python3

"""
Test configuration and shared fixtures for LED strip light controller tests.

Provides common test utilities, fixtures, and mocked dependencies
for testing the LED strip light application without requiring actual hardware.
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from led.color import Color
from led.gpio_service import GPIOService
from led.led_strip_light_controller import LEDStripLightController
from config_manager import ConfigManager


@pytest.fixture
def mock_gpio_service():
    """Mock GPIO service that simulates hardware interactions."""
    mock_service = Mock(spec=GPIOService)
    mock_service.set_pin_pwm = Mock()
    return mock_service


@pytest.fixture
def test_pins():
    """Standard pin configuration for testing."""
    return {
        'red': 18,
        'green': 19, 
        'blue': 20
    }


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager with test data."""
    mock_config = Mock(spec=ConfigManager)
    mock_config.get_all_pin_assignments.return_value = {
        'red': 18,
        'green': 19,
        'blue': 20
    }
    mock_config.get_profile_colors.return_value = (255, 200, 100)
    return mock_config


@pytest.fixture
def led_controller(mock_gpio_service, test_pins):
    """LED controller with mocked GPIO service."""
    return LEDStripLightController(test_pins, gpio_service=mock_gpio_service)


@pytest.fixture
def mock_thread():
    """Mock thread for sequence testing."""
    mock_thread = Mock()
    mock_thread.start = Mock()
    mock_thread.join = Mock()
    mock_thread.name = "test_thread"
    return mock_thread


class TestColors:
    """Collection of test colors for consistent testing."""
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)