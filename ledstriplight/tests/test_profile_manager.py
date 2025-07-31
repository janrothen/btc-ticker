#!/usr/bin/env python3

"""
Tests for the ProfileManager class.

Tests time-based profile management and color retrieval functionality.
"""

import pytest
import datetime
from unittest.mock import Mock, patch
from led.profile_manager import ProfileManager, PROFILE_MORNING, PROFILE_EVENING
from led.color import Color


class TestProfileManager:
    """Test cases for ProfileManager functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager with test profile data."""
        mock_config = Mock()
        mock_config.get_profile_colors.return_value = (255, 200, 100)
        mock_config.get_profile_color_value.return_value = 255
        return mock_config
    
    @pytest.fixture
    def profile_manager(self, mock_config_manager):
        """ProfileManager instance with mocked config."""
        return ProfileManager(mock_config_manager)
    
    def test_profile_manager_creation(self, mock_config_manager):
        """Test ProfileManager can be created with config manager."""
        pm = ProfileManager(mock_config_manager)
        assert pm._config == mock_config_manager
    
    def test_is_morning_before_noon(self, profile_manager):
        """Test morning detection before 12:00."""
        morning_time = datetime.datetime(2023, 7, 30, 8, 30)  # 8:30 AM
        assert profile_manager.is_morning(morning_time) is True
    
    def test_is_morning_at_noon(self, profile_manager):
        """Test morning detection at exactly 12:00."""
        noon_time = datetime.datetime(2023, 7, 30, 12, 0)  # 12:00 PM
        assert profile_manager.is_morning(noon_time) is False
    
    def test_is_morning_after_noon(self, profile_manager):
        """Test morning detection after 12:00."""
        afternoon_time = datetime.datetime(2023, 7, 30, 15, 45)  # 3:45 PM
        assert profile_manager.is_morning(afternoon_time) is False
    
    def test_is_morning_edge_cases(self, profile_manager):
        """Test morning detection edge cases."""
        # Just before noon
        before_noon = datetime.datetime(2023, 7, 30, 11, 59, 59)
        assert profile_manager.is_morning(before_noon) is True
        
        # Just after midnight
        after_midnight = datetime.datetime(2023, 7, 30, 0, 0, 1)
        assert profile_manager.is_morning(after_midnight) is True
    
    @patch('led.profile_manager.datetime')
    def test_get_active_profile_morning(self, mock_datetime, profile_manager):
        """Test getting active profile during morning hours."""
        # Mock current time to be morning
        mock_now = datetime.datetime(2023, 7, 30, 9, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        with patch.object(profile_manager, 'is_morning', return_value=True):
            active_profile = profile_manager.get_active_profile()
            assert active_profile == PROFILE_MORNING
    
    @patch('led.profile_manager.datetime')
    def test_get_active_profile_evening(self, mock_datetime, profile_manager):
        """Test getting active profile during evening hours."""
        # Mock current time to be evening
        mock_now = datetime.datetime(2023, 7, 30, 19, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        with patch.object(profile_manager, 'is_morning', return_value=False):
            active_profile = profile_manager.get_active_profile()
            assert active_profile == PROFILE_EVENING
    
    def test_get_profile_colors(self, profile_manager, mock_config_manager):
        """Test retrieving profile colors."""
        test_colors = (255, 128, 64)
        mock_config_manager.get_profile_colors.return_value = test_colors
        
        colors = profile_manager.get_profile_colors(PROFILE_MORNING)
        
        assert colors == test_colors
        mock_config_manager.get_profile_colors.assert_called_once_with(PROFILE_MORNING)
    
    def test_get_profile_color_value(self, profile_manager, mock_config_manager):
        """Test retrieving specific color value from profile."""
        test_value = 200
        mock_config_manager.get_profile_color_value.return_value = test_value
        
        color_value = profile_manager.get_profile_color_value(PROFILE_EVENING, 'red')
        
        assert color_value == test_value
        mock_config_manager.get_profile_color_value.assert_called_once_with(PROFILE_EVENING, 'red')
    
    def test_get_profile_color_object(self, profile_manager, mock_config_manager):
        """Test retrieving Color object for profile."""
        test_colors = (255, 128, 64)
        mock_config_manager.get_profile_colors.return_value = test_colors
        
        color_obj = profile_manager.get_profile_color_object(PROFILE_MORNING)
        
        assert isinstance(color_obj, Color)
        assert color_obj.rgb == test_colors
        mock_config_manager.get_profile_colors.assert_called_once_with(PROFILE_MORNING)
    
    @patch('led.profile_manager.datetime')
    def test_get_active_profile_color_morning(self, mock_datetime, profile_manager, mock_config_manager):
        """Test getting active profile color during morning."""
        mock_now = datetime.datetime(2023, 7, 30, 8, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        test_colors = (255, 200, 100)
        mock_config_manager.get_profile_colors.return_value = test_colors
        
        with patch.object(profile_manager, 'is_morning', return_value=True):
            color = profile_manager.get_active_profile_color()
            
            assert isinstance(color, Color)
            assert color.rgb == test_colors
            mock_config_manager.get_profile_colors.assert_called_once_with(PROFILE_MORNING)
    
    @patch('led.profile_manager.datetime')
    def test_get_active_profile_color_evening(self, mock_datetime, profile_manager, mock_config_manager):
        """Test getting active profile color during evening."""
        mock_now = datetime.datetime(2023, 7, 30, 20, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        test_colors = (255, 50, 0)
        mock_config_manager.get_profile_colors.return_value = test_colors
        
        with patch.object(profile_manager, 'is_morning', return_value=False):
            color = profile_manager.get_active_profile_color()
            
            assert isinstance(color, Color)
            assert color.rgb == test_colors
            mock_config_manager.get_profile_colors.assert_called_once_with(PROFILE_EVENING)
    
    def test_profile_constants(self):
        """Test that profile constants are defined correctly."""
        assert PROFILE_MORNING == 'profile.morning'
        assert PROFILE_EVENING == 'profile.evening'
    
    def test_config_error_propagation(self, profile_manager, mock_config_manager):
        """Test that configuration errors are properly propagated."""
        # Test that errors from config manager bubble up
        mock_config_manager.get_profile_colors.side_effect = ValueError("Profile not found")
        
        with pytest.raises(ValueError, match="Profile not found"):
            profile_manager.get_profile_colors("invalid.profile")
