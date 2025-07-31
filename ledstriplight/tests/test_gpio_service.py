#!/usr/bin/env python3

"""
Tests for the GPIO service.

Tests GPIO pin control functionality with mocked system calls.
"""

import subprocess
from led.gpio_service import GPIOService


class TestGPIOService:
    """Test cases for GPIO service functionality."""

    def test_gpio_service_creation(self):
        """Test GPIO service can be created."""
        service = GPIOService()
        assert service is not None

    def test_get_pin_pwm_success(self, monkeypatch):
        class DummyResult:
            def __init__(self):
                self.stdout = '128\n'
                self.returncode = 0
        def fake_run(cmd, **kwargs):
            return DummyResult()
        monkeypatch.setattr(subprocess, "run", fake_run)
        service = GPIOService()
        value = service.get_pin_pwm(18)
        assert value == 128

    def test_get_pin_pwm_failure(self, monkeypatch):
        def fake_run_failure(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], "fail")
        monkeypatch.setattr(subprocess, "run", fake_run_failure)
        service = GPIOService()
        value = service.get_pin_pwm(18)
        assert value == -1

    def test_set_pin_pwm(self, monkeypatch):
        called = {}
        def fake_run(cmd, **kwargs):
            called['cmd'] = cmd
            return 0
        monkeypatch.setattr(subprocess, "run", fake_run)
        service = GPIOService()
        service.set_pin_pwm(18, 128)
        assert called['cmd'] == ['pigs', 'p', '18', '128']

    def test_set_pin_pwm_clamping(self, monkeypatch):
        calls = []
        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return 0
        monkeypatch.setattr(subprocess, "run", fake_run)
        service = GPIOService()
        # Test upper bound clamping
        service.set_pin_pwm(18, 300)
        # Test lower bound clamping
        service.set_pin_pwm(18, -10)
        assert ['pigs', 'p', '18', '255'] in calls
        assert ['pigs', 'p', '18', '0'] in calls

    def test_set_pin_pwm_rounding(self, monkeypatch):
        called = {}
        def fake_run(cmd, **kwargs):
            called['cmd'] = cmd
            return 0
        monkeypatch.setattr(subprocess, "run", fake_run)
        service = GPIOService()
        service.set_pin_pwm(18, 127.8)
        assert called['cmd'] == ['pigs', 'p', '18', '128']

    def test_clamp_value_method(self):
        """Test internal value clamping method."""
        service = GPIOService()
        assert service._clamp_value(-10) == 0
        assert service._clamp_value(0) == 0
        assert service._clamp_value(100) == 100
        assert service._clamp_value(127.5) == 128
        assert service._clamp_value(255) == 255
        assert service._clamp_value(300) == 255