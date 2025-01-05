import unittest
from unittest.mock import Mock, patch
from src.devices.siren import SirenDevice
from src.enums.gpio_enums import GPIOType, GPIOState
from src.utils.payload_loader import PayloadLoader


class TestSirenDevice(unittest.TestCase):
    def setUp(self):
        # Mock GPIOService and state change callback
        self.mock_gpio_service = Mock()
        self.mock_mqtt_service = Mock()

        # Device configuration
        self.control_pin = 22
        self.device_id = 4
        self.device_class = "siren"
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
        self.siren_device = SirenDevice(
            device_id=self.device_id,
            device_class=self.device_class,
            gpio_service=self.mock_gpio_service,
            mqtt_service=self.mock_mqtt_service,
            on_state_change=self.mock_state_change_callback,
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_turn_on(self, mock_payload_loader):
        # Simulate the "turn on" command
        self.siren_device.handle_command(PayloadLoader.get(self.device_class, "on"))

        # Assert that the GPIO control pin is toggled
        self.mock_gpio_service.write_pin.assert_called_once_with(self.control_pin, GPIOState.HIGH)

        # Assert that state change is notified
        self.mock_state_change_callback.assert_called_once_with(
            self.device_class, self.device_id, GPIOState.HIGH
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_turn_off(self, mock_payload_loader):
        # Simulate the "close" command
        self.siren_device.handle_command(PayloadLoader.get(self.device_class, "off"))

        # Assert that the GPIO control pin is toggled
        self.mock_gpio_service.write_pin.assert_called_once_with(self.control_pin, GPIOState.LOW)

        # Assert that state change is notified
        self.mock_state_change_callback.assert_called_once_with(
            self.device_class, self.device_id, GPIOState.LOW
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_invalid(self, mock_payload_loader):
        # Simulate an invalid command
        with self.assertRaises(ValueError) as context:
            self.siren_device.handle_command("invalid_command")
        self.assertEqual(
            str(context.exception), f"Unknown command 'invalid_command' for SirenDevice {self.device_id}."
        )

    def test_notify_state_change(self):
        # Call notify_state_change with a specific state
        self.siren_device.notify_state_change("custom_state")

        # Assert the callback is invoked with the correct parameters
        self.mock_state_change_callback.assert_called_once_with(self.device_class, self.device_id, "custom_state")

if __name__ == "__main__":
    unittest.main()
