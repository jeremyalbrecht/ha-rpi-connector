import unittest
from unittest.mock import MagicMock, patch
from src.devices.strip import StripDevice
from src.enums.gpio_enums import GPIOType, GPIOState
from src.utils.payload_loader import PayloadLoader
from tests.unit.services.test_mqtt_service import mqtt_service


class TestStripDevice(unittest.TestCase):

    def setUp(self):
        self.mock_gpio_service = MagicMock()
        self.mock_mqtt_service = MagicMock()
        self.mock_state_change_callback = MagicMock()
        self.control_pin = 5
        self.power_pin = 6
        self.device_id = 4
        self.device_class = "strip"
        self.custom_vars = {
                    "num_leds": 10,
                    "color": (255, 255, 255)
                }
        self.config = [
            {
                "id": self.device_id,
                "class": self.device_class,
                "gpio": [
                    {"name": "control", "gpio": self.control_pin, "type": GPIOType.OUTPUT},
                    {"name": "power", "gpio": self.power_pin, "type": GPIOType.OUTPUT},
                ],
                "env": self.custom_vars
            }]
        self.mock_gpio_service.devices = self.config
        self.custom_vars = {'num_leds': 10, 'color': (255, 255, 255)}
        self.device = StripDevice(
            device_id=self.device_id,
            device_class='strip',
            gpio_service=self.mock_gpio_service,
            mqtt_service=self.mock_mqtt_service,
            on_state_change=self.mock_state_change_callback,
            custom_vars=self.custom_vars)

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_color(self, mock_payload_loader):
        self.device.handle_command(PayloadLoader.get("strip", "color"))
        self.mock_gpio_service.set_strip_color.assert_any_call(self.device._get_gpio("control"), 1, (255, 255, 255))
        self.mock_gpio_service.write_pin.assert_called_once_with(self.power_pin, GPIOState.HIGH)

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_garage_animation(self, mock_payload_loader):
        self.device.handle_command(PayloadLoader.get("strip", "garage_animation"))
        self.mock_gpio_service.write_pin.assert_called_once_with(self.power_pin, GPIOState.HIGH)
        self.assertTrue(self.device.animation_thread.is_alive())

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_handle_command_stop(self, mock_payload_loader):
        self.device.handle_command(PayloadLoader.get("strip", "stop"))
        self.mock_gpio_service.write_pin.assert_called_once_with(self.power_pin, GPIOState.LOW)
        self.mock_gpio_service.set_strip_color.assert_any_call(self.device._get_gpio("control"), 0, (0, 0, 0))

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_get_status_running(self, mock_payload_loader):
        with patch('threading.Thread.is_alive', return_value=True):
            self.device.animation_thread = MagicMock()
            self.assertEqual(self.device.get_status(), PayloadLoader.get("strip", "running"))

    @patch.object(PayloadLoader, "get", side_effect=lambda category, key: f"{category}_{key}")
    def test_get_status_stopped(self, mock_payload_loader):
        self.device.animation_thread = None
        self.assertEqual(self.device.get_status(), PayloadLoader.get("strip", "stopped"))
