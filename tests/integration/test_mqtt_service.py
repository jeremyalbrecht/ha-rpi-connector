# tests/integration/test_mqtt_service.py
import time
import unittest
from unittest.mock import MagicMock, Mock
import paho.mqtt.client as mqtt

from src.devices.garage import GarageDevice
from src.enums.gpio_enums import GPIOType, GPIOState
from src.services.device_service import DeviceService
from src.services.gpio_service import GPIOService
from src.services.mqtt_service import MQTTService
from src.utils.payload_loader import PayloadLoader
from .config import MQTT_BROKER_URL, MQTT_BROKER_PORT

class TestMQTTServiceIntegration(unittest.TestCase):

    def setUp(self):
        # Set up MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, 60)
        self.mqtt_client.loop_start()

        self.gpio_service = GPIOService(devices=[], mock_gpio=True)
        self.received_messages = []

    def tearDown(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()

    def on_message(self, client, userdata, message):
        # Handle incoming MQTT messages
        payload = message.payload.decode('utf-8')
        self.received_messages.append((message.topic, payload))


    def test_mqtt_command_handling(self):
        """Test if commands from the broker are handled correctly by the service."""

        command_topic = "garage/1/set"
        command_payload = "toggle"

        # Create a device mock or instance
        device = GarageDevice(1, "garage", self.gpio_service, Mock())
        device.handle_command = Mock(return_value=None)

        # Setup service with the device
        service = MQTTService(
            host=MQTT_BROKER_URL,
            port=MQTT_BROKER_PORT,
            username="",
            password="",
            devices=[device],
            interval=0
        )

        # Subscribe to the device command topic
        self.mqtt_client.subscribe(command_topic, qos=2)

        service.start()
        time.sleep(2)
        # Publish command
        self.mqtt_client.publish(command_topic, command_payload, qos=2)

        time.sleep(2)
        # Check if the device received the correct command
        assert device.handle_command.call_count == 1

        service.stop()

    def test_mqtt_status_update(self):
        """Test if the service publishes device status updates correctly."""

        status_topic = "garage/1/status"
        device_status = "OPEN"

        # Create a device mock or instance
        device = GarageDevice(1, "garage", self.gpio_service, Mock())
        device.get_status = Mock(return_value=device_status)
        device.get_topic = Mock(return_value=status_topic)

        # Setup service with the device
        service = MQTTService(
            host=MQTT_BROKER_URL,
            port=MQTT_BROKER_PORT,
            username="",
            password="",
            devices=[device],
            interval=2  # Publish status every 2 seconds
        )

        # Subscribe to the device status topic
        self.mqtt_client.subscribe(status_topic, qos=2)

        service.start()
        time.sleep(5)  # Allow time for periodic updates

        # Check if the status message was received
        status_messages = [msg for topic, msg in self.received_messages if topic == status_topic]
        assert len(status_messages) >= 2  # At least 2 messages should have been published
        assert all(msg == device_status for msg in status_messages)  # All messages should match the status

        service.stop()

if __name__ == '__main__':
    unittest.main()