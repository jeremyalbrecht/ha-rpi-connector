import pytest
from unittest.mock import Mock

from src.devices.garage import GarageDevice


@pytest.fixture
def mock_gpio_service():
    gpio_service = Mock()
    gpio_service.read_pin.return_value = 0  # Default to CLOSED state
    return gpio_service

@pytest.fixture
def mock_on_state_change():
    return Mock()

def test_garage_device(mock_gpio_service, mock_on_state_change):
    device = GarageDevice(
        device_id=1,
        device_class="garage",
        gpio_service=mock_gpio_service,
        on_state_change=mock_on_state_change,
    )

    # Test state retrieval
    assert device.get_state() == "closed"

    # Simulate state change
    mock_gpio_service.read_pin.return_value = 1  # OPEN state
    assert device.get_state() == "open"

    # Test command handling
    device.handle_command("OPEN")
    mock_gpio_service.trigger_pin.assert_called_once_with(20)

    # Test manual state change notification
    device.notify_state_change("opening")
    mock_on_state_change.assert_called_with("garage", 1, "opening")