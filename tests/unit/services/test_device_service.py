import pytest
from unittest.mock import Mock
from src.services.device_service import DeviceService
from src.enums.device_class import DEVICE_CLASSES


@pytest.fixture
def sample_config():
    return {
        "devices": [
            {
                "id": 1,
                "class": "garage",
                "gpio": [
                    {"name": "status", "type": "input", "gpio": 18},
                    {"name": "control", "type": "output", "gpio": 20, "default": "high"},
                ],
            },
            {
                "id": 2,
                "class": "garage",
                "gpio": [
                    {"name": "status", "type": "input", "gpio": 27},
                    {"name": "control", "type": "output", "gpio": 21, "default": "high"},
                ],
            },
            {
                "id": 3,
                "class": "motion",
                "gpio": [{"name": "status", "type": "input", "gpio": 4}],
            },
        ],
        "mqtt": {"host": "localhost", "port": 1883, "username": "", "password": ""},
    }


@pytest.fixture
def mock_gpio_service():
    return Mock()


@pytest.fixture
def mock_mqtt_service():
    mock_service = Mock()
    mock_service.handle_device_state_change = Mock()
    return mock_service


@pytest.fixture
def mock_device_classes():
    class MockGarageDevice:
        def __init__(self, device_id, device_class, gpio_service, on_state_change):
            self.device_id = device_id
            self.device_class = device_class
            self.gpio_service = gpio_service
            self.on_state_change = on_state_change

    class MockMotionDevice:
        def __init__(self, device_id, device_class, gpio_service, on_state_change):
            self.device_id = device_id
            self.device_class = device_class
            self.gpio_service = gpio_service
            self.on_state_change = on_state_change

    DEVICE_CLASSES["garage"] = MockGarageDevice
    DEVICE_CLASSES["motion"] = MockMotionDevice


def test_device_service_initialization(sample_config, mock_gpio_service, mock_mqtt_service, mock_device_classes):
    service = DeviceService(sample_config, mock_gpio_service, mock_mqtt_service)

    # Ensure all devices are initialized
    assert len(service.devices) == 3

    # Check if devices are properly initialized
    garage_device = service.devices[0]
    assert garage_device.device_id == 1
    assert garage_device.device_class == "garage"
    assert garage_device.gpio_service == mock_gpio_service
    assert garage_device.on_state_change == mock_mqtt_service.handle_device_state_change

    motion_device = service.devices[2]
    assert motion_device.device_id == 3
    assert motion_device.device_class == "motion"
    assert motion_device.gpio_service == mock_gpio_service
    assert motion_device.on_state_change == mock_mqtt_service.handle_device_state_change


def test_device_service_unsupported_device_class(sample_config, mock_gpio_service, mock_mqtt_service):
    # Add an unsupported device class
    sample_config["devices"].append({"id": 4, "class": "unsupported", "gpio": []})

    with pytest.raises(ValueError) as excinfo:
        DeviceService(sample_config, mock_gpio_service, mock_mqtt_service)

    assert "Unsupported device class: unsupported" in str(excinfo.value)


def test_device_service_no_devices(mock_gpio_service, mock_mqtt_service):
    empty_config = {"devices": []}
    service = DeviceService(empty_config, mock_gpio_service, mock_mqtt_service)

    # Ensure no devices are initialized
    assert len(service.devices) == 0
