import unittest
from unittest.mock import Mock, patch
from src.devices.garage import GarageDevice
from src.enums.gpio_enums import GPIOType, GPIOState
from src.utils.payload_loader import PayloadLoader


class TestGarageDevice(unittest.TestCase):
    def setUp(self):
        # Mock GPIOService and state change callback
        self.mock_gpio_service = Mock()

        # Device configuration
        self.device_id = 1
        self.device_class = "garage"
        self.control_pin = 18
        self.status_pin = 17
        self.config = [
        {
            "id": self.device_id,
            "class": self.device_class,
            "gpio": [
                {"name": "status", "gpio": self.status_pin, "type": GPIOType.OUTPUT, "default": GPIOState.LOW},
                {"name": "control", "gpio": self.control_pin, "type": GPIOType.INPUT},
            ],
        }]
        self.mock_gpio_service.devices = self.config
        self.mock_state_change_callback = Mock()

        # Instantiate the GarageDevice
        self.garage_device = GarageDevice(
            device_id=self.device_id,
            device_class=self.device_class,
            gpio_service=self.mock_gpio_service,
            on_state_change=self.mock_state_change_callback,
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_generate_identifier(self, mock_payload_loader):
        assert self.garage_device.identifier() == f"{self.device_class}_{self.device_id}"

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_open(self, mock_payload_loader):
        # Simulate the "open" command
        self.garage_device.handle_command(PayloadLoader.get("garage", "open"))

        # Assert that the GPIO control pin is toggled
        self.mock_gpio_service.toggle_pin.assert_called_once_with(self.control_pin, 0.5)

        # Assert that state change is notified
        self.mock_state_change_callback.assert_called_once_with(
            self.device_class, self.device_id, "garage_state_opening"
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_close(self, mock_payload_loader):
        # Simulate the "close" command
        self.garage_device.handle_command(PayloadLoader.get("garage", "close"))

        # Assert that the GPIO control pin is toggled
        self.mock_gpio_service.toggle_pin.assert_called_once_with(self.control_pin, 0.5)

        # Assert that state change is notified
        self.mock_state_change_callback.assert_called_once_with(
            self.device_class, self.device_id, "garage_state_closing"
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_invalid(self, mock_payload_loader):
        # Simulate an invalid command
        with self.assertRaises(ValueError) as context:
            self.garage_device.handle_command("invalid_command")
        self.assertEqual(
            str(context.exception), "Unknown command 'invalid_command' for GarageDevice 1."
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_get_status_open(self, mock_payload_loader):
        # Simulate the GPIO service returning HIGH (1) for the status pin
        self.mock_gpio_service.read_pin.return_value = 1

        # Call get_status
        status = self.garage_device.get_status()

        # Assert the correct state is returned
        self.assertEqual(status, "garage_state_open")

        # Assert the status pin is read
        self.mock_gpio_service.read_pin.assert_called_once_with(self.status_pin)

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_get_status_close(self, mock_payload_loader):
        # Simulate the GPIO service returning LOW (0) for the status pin
        self.mock_gpio_service.read_pin.return_value = 0

        # Call get_status
        status = self.garage_device.get_status()

        # Assert the correct state is returned
        self.assertEqual(status, "garage_state_close")

        # Assert the status pin is read
        self.mock_gpio_service.read_pin.assert_called_once_with(self.status_pin)

    def test_notify_state_change(self):
        # Call notify_state_change with a specific state
        self.garage_device.notify_state_change("custom_state")

        # Assert the callback is invoked with the correct parameters
        self.mock_state_change_callback.assert_called_once_with(self.device_class, self.device_id, "custom_state")

    def test_notify_state_change_with_default_status(self):
        # Mock get_status to return a default state
        self.garage_device.get_status = Mock(return_value="default_state")

        # Call notify_state_change without specifying a state
        self.garage_device.notify_state_change()

        # Assert the callback is invoked with the default state
        self.mock_state_change_callback.assert_called_once_with(self.device_class, self.device_id, "default_state")


if __name__ == "__main__":
    unittest.main()
