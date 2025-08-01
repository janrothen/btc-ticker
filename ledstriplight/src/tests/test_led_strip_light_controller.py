#!/usr/bin/env python3

"""
Tests for the LED strip light controller.

Tests LED control functionality with mocked GPIO hardware.
"""

import pytest
from unittest.mock import Mock, patch
from led.led_strip_light_controller import LEDStripLightController
from led.color import Color


class TestLEDStripLightController:

    @pytest.mark.parametrize("r,g,b,expected", [
        (255, 255, 255, 100),
        (0, 0, 0, 0),
        (255, 0, 0, pytest.approx(29, abs=1)),
        (0, 255, 0, pytest.approx(59, abs=1)),
        (0, 0, 255, pytest.approx(12, abs=1)),
    ])
    def test_get_brightness_percentage(self, mock_gpio_service, test_pins, r, g, b, expected):
        mock_gpio_service.get_pin_pwm.side_effect = lambda pin: {test_pins['red']: r, test_pins['green']: g, test_pins['blue']: b}[pin]
        controller = LEDStripLightController(test_pins, mock_gpio_service)
        assert controller.get_brightness_percentage() == expected

    @pytest.mark.parametrize("initial,brightness,expected", [
        ((255, 255, 255), 50, (127, 127, 127)),
        ((0, 0, 0), 80, (204, 204, 204)),
        ((255, 0, 0), 20, (51, 0, 0)),
    ])
    def test_set_brightness(self, mock_gpio_service, test_pins, initial, brightness, expected):
        # Setup initial color
        state = {test_pins['red']: initial[0], test_pins['green']: initial[1], test_pins['blue']: initial[2]}
        def fake_get_pin_pwm(pin):
            return state[pin]
        def fake_set_pin_pwm(pin, value):
            state[pin] = value
        mock_gpio_service.get_pin_pwm.side_effect = fake_get_pin_pwm
        mock_gpio_service.set_pin_pwm.side_effect = fake_set_pin_pwm
        controller = LEDStripLightController(test_pins, mock_gpio_service)
        controller.set_brightness(brightness)
        assert (state[test_pins['red']], state[test_pins['green']], state[test_pins['blue']]) == expected

    def test_set_brightness_invalid(self, mock_gpio_service, test_pins):
        controller = LEDStripLightController(test_pins, mock_gpio_service)
        with pytest.raises(ValueError):
            controller.set_brightness(-1)
        with pytest.raises(ValueError):
            controller.set_brightness(101)
    """Test cases for LED strip light controller."""
    
    def test_controller_creation(self, mock_gpio_service, test_pins):
        """Test controller can be created with dependencies."""
        controller = LEDStripLightController(test_pins, mock_gpio_service)
        
        assert controller._pins == test_pins
        assert controller._gpio_service == mock_gpio_service
        assert controller._interrupt is False
        assert controller._sequence is None
    
    def test_set_color(self, led_controller, mock_gpio_service):
        """Test setting LED color."""
        red_color = Color(255, 0, 0)
        led_controller.set_color(red_color)
        
        # Verify GPIO calls were made for each color channel
        expected_calls = [
            (18, 255),  # Red pin
            (19, 0),    # Green pin  
            (20, 0)     # Blue pin
        ]
        
        actual_calls = [call.args for call in mock_gpio_service.set_pin_pwm.call_args_list]
        assert actual_calls == expected_calls
    
    def test_switch_on(self, led_controller, mock_gpio_service):
        """Test switching LED strip light on."""
        led_controller.switch_on()
        
        # Should set to white (255, 255, 255)
        expected_calls = [
            (18, 239),  # Red pin
            (19, 138),  # Green pin
            (20, 51)   # Blue pin
        ]
        
        actual_calls = [call.args for call in mock_gpio_service.set_pin_pwm.call_args_list]
        assert actual_calls == expected_calls
    
    def test_switch_off(self, led_controller, mock_gpio_service):
        """Test switching LED strip light off."""
        led_controller.switch_off()
        
        # Should set to black (0, 0, 0) and manage interrupt state
        expected_calls = [
            (18, 0),    # Red pin
            (19, 0),    # Green pin
            (20, 0)     # Blue pin
        ]
        
        actual_calls = [call.args for call in mock_gpio_service.set_pin_pwm.call_args_list]
        assert actual_calls == expected_calls
    
    def test_interrupt_control(self, led_controller):
        """Test interrupt state management."""
        assert not led_controller.is_interrupted()
        
        led_controller.interrupt()
        assert led_controller.is_interrupted()
        
        led_controller.resume()
        assert not led_controller.is_interrupted()
    
    @patch('led.led_strip_light_controller.Thread')
    def test_start_sequence(self, mock_thread_class, led_controller):
        """Test starting a sequence."""
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread
        
        def dummy_effect():
            pass
        
        led_controller.start_sequence(dummy_effect, "arg1", "arg2", kwarg1="value1")
        
        # Verify thread was created with correct arguments
        mock_thread_class.assert_called_once_with(
            target=dummy_effect, 
            args=("arg1", "arg2"), 
            kwargs={"kwarg1": "value1"}
        )
        mock_thread.start.assert_called_once()
        assert led_controller._sequence == mock_thread
        assert not led_controller.is_interrupted()
    
    def test_stop_sequence_no_sequence(self, led_controller):
        """Test stopping when no sequence is running."""
        # Should not raise an error when no sequence is running
        led_controller.stop_current_sequence()
        assert led_controller._sequence is None
    
    @patch('led.led_strip_light_controller.Thread')
    def test_run_sequence(self, mock_thread_class, led_controller):
        """Test running a sequence (stop + start)."""
        mock_thread = Mock()
        mock_thread.name = "test_sequence"
        mock_thread_class.return_value = mock_thread
        
        def dummy_effect():
            pass
        
        led_controller.run_sequence(dummy_effect, "test_arg")
        
        mock_thread_class.assert_called_once_with(
            target=dummy_effect,
            args=("test_arg",),
            kwargs={}
        )
        mock_thread.start.assert_called_once()