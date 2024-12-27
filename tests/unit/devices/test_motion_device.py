import unittest
from unittest.mock import Mock, patch

from src.devices.motion import MotionDevice
from src.enums.gpio_enums import GPIOType, GPIOState
from src.utils.payload_loader import PayloadLoader


class TestMotionDevice(unittest.TestCase):
    def setUp(self):
        # Mock GPIOService and state change callback
        self.mock_gpio_service = Mock()

        # Device configuration
        self.status_pin = 3
        self.device_id = 5
        self.device_class = "motion"
        self.config = [
        {
            "id": self.device_id,
            "class": self.device_class,
            "gpio": [
                {"name": "status", "gpio": self.status_pin, "type": GPIOType.INPUT},
            ],
        }]
        self.mock_gpio_service.devices = self.config
        self.mock_state_change_callback = Mock()


        # Instantiate the GarageDevice
        self.motion_device = MotionDevice(
            device_id=self.device_id,
            device_class=self.device_class,
            gpio_service=self.mock_gpio_service,
            on_state_change=self.mock_state_change_callback,
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_should_fail(self, mock_payload_loader):
        # Simulate an invalid command
        with self.assertRaises(ValueError) as context:
            self.motion_device.handle_command("invalid_command")
        self.assertEqual(
            str(context.exception), f"MotionDevice is a read-only device."
        )

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_status_is_fetched(self, mock_payload_loader):
        self.motion_device.get_status()

        # Assert the callback is invoked with the correct parameters
        self.mock_gpio_service.read_pin.assert_called_once_with(self.status_pin)

if __name__ == "__main__":
    unittest.main()
