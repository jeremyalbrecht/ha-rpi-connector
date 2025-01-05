import json
import unittest
from unittest.mock import Mock, patch
from src.devices.light import LightDevice
from src.enums.gpio_enums import GPIOType, GPIOState
from src.utils.payload_loader import PayloadLoader


class TestLightDevice(unittest.TestCase):
    def setUp(self):
        # Mock GPIOService and state change callback
        self.mock_gpio_service = Mock()
        self.mock_mqtt_service = Mock()

        # Device configuration
        self.control_pin = 18
        self.device_id = 3
        self.device_class = "light"
        self.config = [
        {
            "id": self.device_id,
            "class": self.device_class,
            "gpio": [
                {"name": "control", "gpio": self.control_pin, "type": GPIOType.OUTPUT},
            ],
        }]
        self.mock_gpio_service.devices = self.config
        self.mock_state_change_callback = Mock()


        # Instantiate the GarageDevice
        self.light_device = LightDevice(
            device_id=self.device_id,
            device_class=self.device_class,
            gpio_service=self.mock_gpio_service,
            mqtt_service=self.mock_mqtt_service,
            on_state_change=self.mock_state_change_callback,
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_turn_on(self, mock_payload_loader):
        # Simulate the "turn on" command
        self.light_device.handle_command(json.dumps({"state": PayloadLoader.get("light", "open")}))

        # Assert that the GPIO control pin is toggled
        self.mock_gpio_service.write_pin.assert_called_once_with(self.control_pin, GPIOState.HIGH)

        # Assert that state change is notified
        self.mock_state_change_callback.assert_called_once_with(
            self.device_class, self.device_id, json.dumps({"state": PayloadLoader.get("light", "open")})
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_turn_off(self, mock_payload_loader):
        # Simulate the "close" command
        self.light_device.handle_command(json.dumps({"state": PayloadLoader.get("light", "close")}))

        # Assert that the GPIO control pin is toggled
        self.mock_gpio_service.write_pin.assert_called_once_with(self.control_pin, GPIOState.LOW)

        # Assert that state change is notified
        self.mock_state_change_callback.assert_called_once_with(
            self.device_class, self.device_id, json.dumps({"state": PayloadLoader.get("light", "close")})
        )

    def test_notify_state_change(self):
        # Call notify_state_change with a specific state
        self.light_device.notify_state_change("custom_state")

        # Assert the callback is invoked with the correct parameters
        self.mock_state_change_callback.assert_called_once_with(self.device_class, self.device_id, "custom_state")

if __name__ == "__main__":
    unittest.main()
