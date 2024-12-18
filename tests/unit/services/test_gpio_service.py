import logging
import pytest
from unittest.mock import patch, call
from src.services.gpio_service import GPIOService
from src.enums.gpio_enums import GPIOType, GPIOState

@pytest.fixture
def mock_devices():
    """Fixture to provide a mock device list."""
    return [
        {
            "id": "device_1",
            "gpio": [
                {"gpio": 17, "type": GPIOType.OUTPUT, "default": GPIOState.LOW},
                {"gpio": 18, "type": GPIOType.INPUT},
            ],
        },
        {
            "id": "device_2",
            "gpio": [
                {"gpio": 22, "type": GPIOType.OUTPUT, "default": GPIOState.HIGH},
            ],
        },
    ]

@pytest.fixture
def mock_logger():
    """Fixture to mock the logger."""
    with patch("src.services.gpio_service.logger") as mock_logger:
        yield mock_logger

@pytest.fixture
def gpio_service_with_mock(mock_devices):
    """Fixture to initialize GPIOService in mock mode."""
    return GPIOService(devices=mock_devices, mock_gpio=True)

def test_gpio_service_initialization(mock_logger, gpio_service_with_mock):
    """Test GPIOService initialization with mocked GPIO."""
    assert gpio_service_with_mock.mock_gpio is True

    # Assert logs during initialization
    expected_calls = [
        call("Configuring pin 17 as GPIOType.OUTPUT for device ID device_1"),
        call("Configuring pin 18 as GPIOType.INPUT for device ID device_1"),
        call("Configuring pin 22 as GPIOType.OUTPUT for device ID device_2"),
    ]
    mock_logger.debug.assert_has_calls(expected_calls, any_order=True)

def test_gpio_service_read_pin(mock_logger, gpio_service_with_mock):
    """Test reading a GPIO pin in mock mode."""
    result = gpio_service_with_mock.read_pin(17)
    assert result == 0  # Default mock return value

    # Assert log for reading pin
    mock_logger.debug.assert_has_calls([call("Mock read GPIO pin 17")])

def test_gpio_service_write_pin(mock_logger, gpio_service_with_mock):
    """Test writing to a GPIO pin in mock mode."""
    gpio_service_with_mock.write_pin(22, "high")

    # Assert log for writing pin
    mock_logger.debug.assert_has_calls([call("Mock write GPIO pin 22 to high")])

def test_gpio_service_toggle_pin(mock_logger, gpio_service_with_mock):
    """Test toggling a GPIO pin in mock mode."""
    gpio_service_with_mock.toggle_pin(18, duration=0.5)

    # Assert log for toggling pin
    mock_logger.debug.assert_has_calls([call("Mock toggle GPIO pin 18")])

def test_gpio_service_cleanup(mock_logger, gpio_service_with_mock):
    """Test GPIO cleanup in mock mode."""
    gpio_service_with_mock.cleanup()

    # Assert log for cleanup
    mock_logger.debug.assert_has_calls([call("Cleaning up GPIO resources")])
